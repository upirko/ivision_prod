import asyncio
import os
import logging
import threading
import websockets
from websockets import WebSocketServerProtocol
import json
from video_processing import process_video_stream
from utils import STREAMS
import redis

REDIS_HOST = os.getenv('REDIS_HOST', None)
REDIS_PORT = 6379

logging.basicConfig(level=logging.INFO)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def send_data(event_type, payload):
    data = {'event': event_type, 'payload': payload}
    return json.dumps(data)

class Server:

    def __init__(self, host, port):
        self.clients = list()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        server = websockets.serve(self.websocket_handler, host, port)
        infinity_clients = threading.Thread(target=asyncio.run, args=(self.infinity_clients_goround(), ))
        infinity_clients.start()
        loop.run_until_complete(server)
        loop.run_forever()

    async def register(self, websocket):
        client = dict()
        client['client'] = websocket
        self.clients.append(client)
        logging.info(f'Register client: {websocket.remote_address}')
        await self.send(send_data('init', STREAMS), websocket)
    
    async def unregister(self, websocket):
        logging.info(f'Unregister client...\n')
        for client in self.clients:
            if client.get('client', None) == websocket:
                self.clients.remove(client)
        logging.info(f'Clients size after removing: {len(self.clients)}')

    async def send(self, message, client):
        try:
            await asyncio.wait([client.send(message)])
        except:
            logging.error('Connection was closed\n')

    async def websocket_handler(self, websocket, url):
        logging.info("Initializing registration of websocket client...\n")
        await self.register(websocket)
        try:
            await self.distribute(websocket)
        finally:
            await self.unregister(websocket)
    
    async def distribute(self, websocket):
        async for message in websocket:
            data = json.loads(message)
            logging.info(f'Clients size: {len(self.clients)}\n')
            event = data.get('event', None)
            if event is not None and event == 'changeStream':
                for client in self.clients:
                    if client.get('client') == websocket:
                        client['streamId'] = data.get('payload', None)
                        break

    async def infinity_clients_goround(self):
        logging.info('Come to you once')
        while True:
            if self.clients:
                for client in self.clients:
                    streamId = client.get('streamId', None)
                    client_ = client.get('client', None)
                    if client_ is not None and streamId is not None:
                        streamId_ = r.get(streamId)
                        if streamId_ is not None:
                            data = json.loads(streamId_)
                            await self.send(send_data('update', data), client_)
                await asyncio.sleep(0.2)
