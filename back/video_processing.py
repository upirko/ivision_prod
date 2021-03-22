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

def process_video_stream(index, video_src):
    logging.info(f'Start processing stream: {video_src}')
    video_capture = cv.VideoCapture(video_src)
    video_capture.set(cv.CAP_PROP_BUFFERSIZE, 1)
    video_capture.set(cv.CAP_PROP_FPS, 2)
    video_capture.set(cv.CAP_PROP_POS_FRAMES , 1)
    FPS = video_capture.get(cv.CAP_PROP_FPS)
    wait_ms = int((1000/FPS) * (FPS-1))
    cur_time = int(round(time.time() * 1000))
    while True:
        if video_capture.isOpened():
            if (int(round(time.time() * 1000)) >= cur_time + wait_ms):
                ret, frame = video_capture.read()
                width_  = video_capture.get(cv.CAP_PROP_FRAME_WIDTH)   # float `width`
                height_ = video_capture.get(cv.CAP_PROP_FRAME_HEIGHT)
                coords = list()
                classes, _, boxes = dm.detect(frame, confThreshold=0.1, nmsThreshold=0.4)
                cars = []       
                for classId, box in zip(classes, boxes):
                    if object_names[classId[0]] in ['car', 'bus', 'train', 'motorbike', 'truck']:
                        box = [b for b in box.tolist()] 
                        cars.append(box)
                
                newStage = list()
                x_center = 0
                y_center = 0
                for stream in STREAMS:
                    if stream.get('source') == video_src:
                        x_start, y_start = stream.get('roi')[0]
                        x1_start, y1_start = stream.get('roi')[1]

                        x_start *= width_
                        x1_start *= width_
                        y_start *=height_
                        y1_start *=height_


                        x_avg_start = (x_start + x1_start)/2

                        x_end, y_end = stream.get('roi')[2]
                        x1_end, y1_end = stream.get('roi')[3]
                        x_end *= width_
                        x1_end *= width_
                        y_end *=height_
                        y1_end *=height_

                        area = [x1_start, y1_start, x1_end, y1_end]
                        logging.info(f'area {area}\n')
                        # x_avg_end = (x_end + x1_end)/2
                        true_cars = list()
                        for car in cars:
                            x_car, y_car, width, height = box
                            car_area = [x_car, y_car, x_car+width, y_car+height]
                            # if stream.get('source') == "https://s2.moidom-stream.ru/s/public/0000010493.m3u8":

                            # center_x = (x_car + width) /2 
                            # center_y = (y_car + height) /2 

                            # logging.info(f'car:{x_car},{y_car}')
                            # logging.info(f'coord:{x_avg_start},{x_avg_end}')
                            logging.info(f'car_area {car_area}\n')
                            if is_cross(area, car_area):
                                true_cars.append(car)

                            # if(x_avg_start>=center_x and center_x<=x_avg_end):
                                # if(y_start >=  center_y and center_y <= y1_end):
                                    # true_cars.append(car)
                                    # if strвeam.get('source') == "https://s2.moidom-stream.ru/s/public/0000010493.m3u8":
                                        # logging.info(f'true:{true_cars}')


                        # if len(true_cars)!=0:
                        #     newStage.append([x_start,y_start,0.1,y1_start])
                        #     for car in true_cars:
                        #         newStage.append(car)
                        #     newStage.append([x_end,y_end,0.1,y_end])


                        # logging.info(f'coord:{true_cars}')

                        # x_center = x_avg_start
                        # y_center =y1_start/2
                # logging.info(f'coord:{newStage}')
                # i = 0
                # cars = true_cars
                # logging.info(f'privet {cars}\n')
                # logging.info(f'privet1 {true_cars}\n')
                if(len(cars)!=0):
                    # while i < len(cars) - 1:
                    #     j = 0
                    #     while j < len(cars) - 1 - i:
                    #         x, y, width, height = cars[j]
                    #         x1, y1, width1, height1 = cars[j+1]

                    #         x_real = x/width_ + width/2
                    #         y_real = height/2

                    #         x_real1 = x1/width_+ width1/2
                    #         y_real1 = height1/2

                    #         hypotenuse = pow(pow((x_center + x_real),2)+ pow((y_real),2), (1/2))
                    #         hypotenuse1 = pow(pow((x_center + x_real1),2) + pow((y_real1),2), (1/2))

                    #         if  hypotenuse > hypotenuse1:
                    #             cars[j], cars[j+1] = cars[j+1], cars[j]
                    #         j += 1
                    #     i += 1

                    # i = 0
                    # logging.info(f'privet1\n')
                    # cars_updated=[]
                    # while i < len(cars)-1:
                    #     x, y, width, height = cars[i]
                    #     cars_updated.append([x, y, width, height, 'true'])

                    #     x1, y1, width1, height1 = cars[i+1]
            
                    #     x_real = x/width_ + width/2
                    #     y_real = height/2

                    #     x_real1 = x1/width_+ width1/2
                    #     y_real1 = height1/2
                    #     hypotenuse = pow(pow((x_real + x_real1),2)+ pow((y_real+y_real1),2), (1/2))
                
                    #     avg_width = 0
                    #     avg_height = 0
                    #     if width != 0 & width1 !=0:
                    #        avg_width = (width + width1)/2
                    #     if width == 0:
                    #         avg_width = width1
                    #     else:
                    #         avg_width = width
                    #     avg_height = (height+ height1)/2
                    #     cars_cnt = math.floor(hypotenuse/width)

                    #     k = 1
                    #     while k<= cars_cnt+1:
                    #         cars_updated.append([(x+avg_width)*k, y+avg_height, avg_width, avg_height, 'false'])
                    #         k+=1
                    #     i += 1


                    for box in true_cars:
                        x, y, width, height = box
                        coords.append({
                            'x': x/width_,
                            'y': y/height_,
                            'width': width/width_,
                            'height': height/height_
                        })
                        r.set(index, json.dumps({'video_src': video_src, 'coords': coords}))
                        # logging.info(f'coord:{coords}')
                
                # for classId, box in zip(classes, boxes):
                #     if object_names[classId[0]] in ['car', 'bus', 'train', 'motorbike', 'truck']:
                #         box = [b for b in box.tolist()] 
                #         x, y, width, height = box
                #         coords.append({
                #             'x': x/width_,
                #             'y': y/height_,
                #             'width': width/width_,
                #             'height': height/height_
                #         })
                # r.set(index, json.dumps({'video_src': video_src, 'coords': coords}))
                # logging.info(f'privet3\n')
                cur_time += wait_ms
            # time.sleep(10)

def isRectangleOverlap(R1, R2):
    if (R1[0]>=R2[2]) or (R1[2]<=R2[0]) or (R1[3]<=R2[1]) or (R1[1]>=R2[3]):
        return False
    else:
        return True

def is_cross(a,b):
    ax1,ay1,ax2,ay2 = a[0],a[1],a[2],a[3]          # прямоугольник А 
    bx1, by1, bx2, by2 = b[0], b[1], b[2], b[3]    # прямоугольник B
    # это были координаты точек диагонали по каждому прямоугольнику

    # 1. Проверить условия перекрытия, например, если XПA<XЛB , 
    #    то прямоугольники не пересекаются,и общая площадь равна нулю.
    #   (это случай, когда они справа и слева) и аналогично, если они сверху
    #    и снизу относительно друг друга.   
    #    (XПА - это  Х Правой точки прямоугольника А)
    #    (ХЛВ - Х Левой точки прямоугольника В )
    #    нарисуй картинку (должно стать понятнее)

    xA = [ax1,ax2]  # координаты x обеих точек прямоугольника А
    xB = [bx1,bx2]  # координаты x обеих точке прямоугольника В

    yA = [ay1, ay2]  # координаты x обеих точек прямоугольника А
    yB = [by1, by2]  # координаты x обеих точек прямоугольника В

    if max(xA)<min(xB) or max(yA) < min(yB) or min(yA) > max(yB):
        return False    # не пересекаются

    # 2. Определить стороны прямоугольника образованного пересечением,
    # например,
    # если XПA>XЛB, а XЛA<XЛB, то ΔX=XПA−XЛB

    elif max(xA)>min(xB) and min(xA)<min(xB):
        dx = max(xA)-min(xB)
        return True     # пересекаются
    else:
        return True     # пересекаются
