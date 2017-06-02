#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import cv2
import logging
import numpy as np
# 1280*720

import tortoise as t

import turning as turn

t.update_config(TORTOISE_WALK_PERIOD=0.1)
eye = t.peripheral.eye


class BeaconDetectionTask(t.Task):
    logger = logging.getLogger('tortoise.task.beacon')

    def __init__(self):
        super(BeaconDetectionTask, self).__init__()
        self.done = False

        self.beacon_area = None
        self.turn_dir = 'middle'

        self.direction_constant = 2
        self.threshold_area = 140000

    def step(self):
        print '\033[1;36m{}\033[0m'.format('BEACON DETECT START')

        flag = 0
        frame = eye.see()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_color = np.array([150, 80, 80])
        upper_color = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_color, upper_color)

        thresh = cv2.adaptiveThreshold(mask, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

        image, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # img = cv2.drawContours(mask, contours, -1, (0, 255, 0), 3)
        # cv2.imshow('img', img)

        m = []
        cx = 0
        cxi = []
        total_area = []

        for i in range(0, len(contours)):
            m.append(cv2.moments(contours[i]))

        for i in range(0, len(contours)):
            if m[i]['m00'] != 0:
                total_area.append(cv2.contourArea(contours[i]))
            else:
                total_area.append(0)
        total_area.sort(reverse=True)

        area_max = total_area[0]
        total_area.pop(0)
        self.beacon_area = total_area_n1 = sum(total_area)

        for i in range(0, len(contours)):
            if m[i]['m00'] != 0:
                if cv2.contourArea(contours[i]) == area_max:
                    continue
                else:
                    cxi.append(int(m[i]['m10'] / m[i]['m00'] * cv2.contourArea(contours[i]) / total_area_n1))
            else:
                cxi.append(0)

        for i in range(0, len(cxi)):
            cx = cxi[i] + cx

        # k = cv2.waitKey(5) & 0xFF
        # if k == 27:
        #     break

        picture_size = mask.shape

        error_percent = 0.05  # 1%

        left_boundary = picture_size[1] / self.direction_constant - picture_size[1] * error_percent
        right_boundary = picture_size[1] / self.direction_constant + picture_size[1] * error_percent

        # print picture_size[1]
        # print cx
        # print left_boundary
        # print right_bou

        if total_area_n1 > self.threshold_area:
            self.done = True
        else:
            if left_boundary <= cx <= right_boundary:
                # print 'middle'
                self.logger.info('beacon detected at center')
                self.turn_dir = 'middle'
            elif cx < left_boundary:
                # turn left
                self.logger.info('beacon detected at left')
                self.turn_dir = 'left'
            elif cx > right_boundary:
                # turn right
                self.logger.info('beacon detected at right')
                self.turn_dir = 'right'

        print '\033[1;36m{}\033[0m'.format('BEACON DETECT END')


if __name__ == '__main__':
    tttt = t.Tortoise()
    tttt.task = BeaconDetectionTask()
    tttt.walk()
