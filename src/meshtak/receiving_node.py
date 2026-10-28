from serial.tools import list_ports
import serial, time, threading
import meshtastic.serial_interface
from pubsub import pub
from meshtak.translator import translate_position_to_cot
from meshtak.repository import add_track_to_queue


is_connected = threading.Event()

def try_connect(port, result):
    try:
        result["interface"] = meshtastic.serial_interface.SerialInterface(
            devPath=port
        )
    except Exception as e:
        result["error"] = e

def find_receiver_node():
    for port in list_ports.comports():
        try:
            print(f"Trying {port.device}...")
            ser = serial.Serial(
                port=port.device,
                baudrate=115200,
                timeout=2
            )
            print("Port opened")
            ser.close()

            result = {}

            thread = threading.Thread(
                target=try_connect,
                args=(port.device, result),
                daemon=True
            )

            thread.start()
            thread.join(timeout=5)

            if thread.is_alive():
                print("Connection timed out")
            else:
                is_connected.set()
                return result.get("interface")

        except Exception:
            pass
    return None

def on_receive(packet, interface):
    try:
        decoded = packet.get("decoded", {})
        if decoded.get("portnum") == "POSITION_APP":
            pos = decoded.get("position", {})

            latitude = pos.get("latitude")
            longitude = pos.get("longitude")
            altitude = pos.get("altitude")
            time = pos.get("time")
            from_id = packet.get("fromId")

            track = translate_position_to_cot(
                lattitude=latitude, 
                longitude=longitude, 
                altitude=altitude, 
                fromId=from_id, 
                track_time=time)
            add_track_to_queue(track=track)

    except Exception as e:
        print(e)
        raise e


def on_connection_lost(interface, topic=pub.AUTO_TOPIC):
    is_connected.clear()
    print("Meshtastic connection lost!")

def stop():
    is_connected.clear()
    pub.unsubscribe(on_receive, "meshtastic.receive")
    pub.unsubscribe(on_connection_lost, "meshtastic.connection.lost")

def start():
    while True:
        try:
            interface = find_receiver_node()
            if interface == None:
                print("Failed to find Meshtastic serial conn, retrying in 5 seconds...")
                time.sleep(5)
                continue
            else:
                pub.subscribe(on_receive, "meshtastic.receive")
                pub.subscribe(on_connection_lost, "meshtastic.connection.lost")
                while True:
                    if (is_connected.is_set()):
                        time.sleep(1)
                    else:
                        stop()
                        break
                        
    

        except Exception as ex:
            print(f"Serial connection failed: {ex}")
            stop()
            time.sleep(5)