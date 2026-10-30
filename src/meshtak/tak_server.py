from configparser import ConfigParser
import meshtak.repository as repository
import asyncio, pytak, time

tak_connected = False

config = ConfigParser()

config["tak"] = {
    "COT_URL": "tls://192.168.100.110:8089",
    "PYTAK_TLS_DONT_CHECK_HOSTNAME": "1",
    "PYTAK_TLS_CLIENT_CERT": "/app/certs/meshtak.pem",
    "PYTAK_TLS_CLIENT_KEY": "/app/certs/meshtak.key",
    "PYTAK_TLS_CLIENT_CAFILE": "/app/certs/ca-trusted.pem",
    "PYTAK_TLS_CLIENT_PASSWORD": "atakatak",
    "DEBUG": "0"
}

cfg = config["tak"]


class TakSender(pytak.QueueWorker):

    async def run(self):
        while True:
            payload = await asyncio.to_thread(
                repository.track_blocking_queue.get
            )
            try:
                print("Sending message to PyTAK")
                await self.put_queue(payload)
            except Exception:
                print("Failed to queue TAK message")
                raise
            finally:
                repository.track_blocking_queue.task_done()


async def connect_to_tak_server():
    clitool = None
    try:
        clitool = pytak.CLITool(cfg)
        await clitool.setup()
        clitool.add_tasks({
            TakSender(clitool.tx_queue, cfg)
        })
        print("Connected to TAK Server")
        await clitool.run()
    except asyncio.CancelledError:
        raise
    except Exception:
        print("TAK Server connection encountered an error")
    finally:
        print("TAK connection closed")


async def start():
    while True:
        await connect_to_tak_server()
        print("Retrying TAK connection in 5 seconds...")
        await asyncio.sleep(5)
    
