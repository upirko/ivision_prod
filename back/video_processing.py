import os
import logging
import cv2 as cv
import time
import redis
import json
from utils import STREAMS

REDIS_HOST = os.getenv('REDIS_HOST', None)
REDIS_PORT = 6379

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

logging.basicConfig(level=logging.INFO)

current_directory = os.getcwd()
dm = cv.dnn_DetectionModel(current_directory + '/model/yolov3.cfg', current_directory + '/model/yolov3.weights')
dm.setInputSize(704, 704)
dm.setInputScale(1.0 / 255)
dm.setInputSwapRB(True)

object_names = list()

with open(current_directory + '/model/classes.txt', 'r') as file:
    object_names = [line.strip() for line in file.readlines()]

def process_video_stream(index, video_src):
    logging.info(f'Start processing stream: {video_src}')
    while True:
        video_capture = cv.VideoCapture(video_src)
        video_capture.set(cv.CAP_PROP_BUFFERSIZE, 1)
        video_capture.set(cv.CAP_PROP_FPS, 2)
        video_capture.set(cv.CAP_PROP_POS_FRAMES , 1)
        FPS = 1/30
        FPS_MS = int(FPS * 1000)
        ret, frame = video_capture.read()
        width_  = video_capture.get(cv.CAP_PROP_FRAME_WIDTH)   # float `width`
        height_ = video_capture.get(cv.CAP_PROP_FRAME_HEIGHT)
        coords = list()
        classes, _, boxes = dm.detect(frame, confThreshold=0.1, nmsThreshold=0.4)
        for classId, box in zip(classes, boxes):
            if object_names[classId[0]] in ['car', 'bus', 'train', 'motorbike', 'truck']:
                box = [b for b in box.tolist()] 
                x, y, width, height = box
                coords.append({
                    'x': x/width_,
                    'y': y/height_,
                    'width': width/width_,
                    'height': height/height_
                })
        r.set(index, json.dumps({'video_src': video_src, 'coords': coords}))
        # time.sleep(10)
