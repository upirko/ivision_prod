import os
import logging
import cv2 as cv
import time
import redis
import json
import math
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
    area.append(AREA[1][0] * width_)
    area.append(AREA[1][1] * height_)
    area.append(AREA[3][0] * width_)
    area.append(AREA[3][1] * height_)

    while True:
        if not video_capture.isOpened():
            continue
        
        ret, frame = video_capture.read()
        classes, _, boxes = dm.detect(frame, confThreshold=0.1, nmsThreshold=0.4)

        coords = list()
        for classId, box in zip(classes, boxes):
            if not object_names[classId[0]] in ['car', 'bus', 'train', 'motorbike', 'truck']:
                continue

            x, y, w, h = [b for b in box.tolist()]

            if not is_cross(area, [x, y, x + w, y + h]):
                continue
            
            coords.append({
                'x': x/width_,
                'y': y/height_,
                'width': w/width_,
                'height': h/height_
            })

def is_cross(a,b):
    ax1, ay1, ax2, ay2 = a[0], a[1], a[2], a[3]          # прямоугольник А 
    bx1, by1, bx2, by2 = b[0], b[1], b[2], b[3]    # прямоугольник B
    # это были координаты точек диагонали по каждому прямоугольнику

    # 1. Проверить условия перекрытия, например, если XПA<XЛB , 
    #    то прямоугольники не пересекаются,и общая площадь равна нулю.
    #   (это случай, когда они справа и слева) и аналогично, если они сверху
    #    и снизу относительно друг друга.   
    #    (XПА - это  Х Правой точки прямоугольника А)
    #    (ХЛВ - Х Левой точки прямоугольника В )
    #    нарисуй картинку (должно стать понятнее)

    xA = [ax1, ax2]  # координаты x обеих точек прямоугольника А
    xB = [bx1, bx2]  # координаты x обеих точке прямоугольника В

    yA = [ay1, ay2]  # координаты x обеих точек прямоугольника А
    yB = [by1, by2]  # координаты x обеих точек прямоугольника В

    result = max(xA)<min(xB) or max(yA) < min(yB) or min(yA) > max(yB)
    logging.info(f'CHECK: {a} with {b} = {result}')

    return result
