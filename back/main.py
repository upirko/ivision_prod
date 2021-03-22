import os
import json
from multiprocessing import Process, Manager
import logging
import threading
import websockets
from server import Server
from video_processing import process_video_stream
from utils import STREAMS
import threading
from server import Server

logging.basicConfig(level=logging.INFO)
HOST = os.getenv('HOST', None)
PORT = os.getenv('PORT', None)

if __name__ == '__main__':
    if HOST is None or PORT is None:
        logging.error('Make sure that you defined PORT or HOST value')
        exit(1)
    
    processes = list()
    for i in range(1):
        p = Process(target=process_video_stream, args=(i, ))
        p.start()
        processes.append(p)
    server = Server(HOST, PORT)

