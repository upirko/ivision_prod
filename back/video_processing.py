import os
import logging
import cv2 as cv
import time
import redis
import json
import math
import numpy as np
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

def process_video_stream(index):
    AREA = STREAMS[index].get('roi')
    video_src = STREAMS[index].get('source')

    logging.info(f'Start processing stream: {video_src}')
    video_capture = cv.VideoCapture(video_src)
    video_capture.set(cv.CAP_PROP_BUFFERSIZE, 1)
    video_capture.set(cv.CAP_PROP_FPS, 2)
    video_capture.set(cv.CAP_PROP_POS_FRAMES , 1)
    width_  = video_capture.get(cv.CAP_PROP_FRAME_WIDTH)
    height_ = video_capture.get(cv.CAP_PROP_FRAME_HEIGHT)

    area = list()
    for point in AREA:
        area.append([int(point[0] * width_), int(point[1] * height_)])

    pts = np.array(area)
    pts_mask = pts - pts.min(axis=0)
    rect = cv.boundingRect(pts)
    x_,y_,w_,h_ = rect

    while True:
        if not video_capture.isOpened():
            continue
        
        ret, frame = video_capture.read()
        croped = frame[y_:y_+h_, x_:x_+w_].copy()
        mask = np.zeros(croped.shape[:2], np.uint8)
        cv.drawContours(mask, [pts_mask], -1, (255, 255, 255), -1, cv.LINE_AA)
        dst = cv.bitwise_and(croped, croped, mask=mask)

        classes, _, boxes = dm.detect(dst, confThreshold=0.1, nmsThreshold=0.4)

        coords = list()
        for classId, box in zip(classes, boxes):
            if not object_names[classId[0]] in ['car', 'bus', 'train', 'motorbike', 'truck']:
                continue

            x, y, w, h = [b for b in box.tolist()]

            x = x + x_
            y = y + y_
            
            coords.append({
                'x': x/width_,
                'y': y/height_,
                'width': w/width_,
                'height': h/height_
            })
        r.set(index, json.dumps(coords))
