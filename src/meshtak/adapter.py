import asyncio, threading
import meshtak.tak_server as tak_server
import meshtak.receiving_node as receiving_node
import webserver.web_server as web_server

def start_adapter():
    tak_thread = threading.Thread(target=start_tak_server, daemon=True)
    tak_thread.start()
    receiving_node_thread = threading.Thread(target=start_receiver_node, daemon=True)
    receiving_node_thread.start()
    web_server_thread = threading.Thread(target=launch_web_server, daemon=True)
    web_server_thread.start()
    try:
        tak_thread.join()
        receiving_node_thread.join()
        web_server_thread.join()

    except KeyboardInterrupt:
        print("Shutting down...")

def start_tak_server():
    print("Starting TAK server...")
    try:
        asyncio.run(tak_server.start())
    except Exception as e:
        print(f"TAK server error: {e}")

def start_receiver_node():
    rn = receiving_node.RecieverNode()
    rn.start()

def launch_web_server():
    web_server.start()