#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import math

import sys

import tortoise as t
import tool

# import recording

import turning as turn

import time

# unit: mm, min: 50mm, max: 500mm
t.update_config(TORTOISE_WALK_PERIOD = 0.1)


# def distance():
#     # while True:
#     st = time.time()
#     distance_set_raw = [0, 0, 0, 0, 0]
#     for i in range(5):
#         print "%9.0f" % d.get(i),
#         distance_set_raw[i] = d.get(i)
#     ed = time.time()
#     print '   ', st - ed
#     # time.sleep(1)
#     return distance_set_raw


def duration2times(duration):
    return int(math.ceil(duration/float(t.config.TORTOISE_WALK_PERIOD)))


def setlr_closure(l, r):
    def func():
        t.p.wheels.lr = l, r

    return func


class PlanterWallFollower(t.Task):
    def __init__(self):
        super(PlanterWallFollower, self).__init__()
        self.done = False

        self.step_manager = tool.StepManager()

    def step(self):
        if self.step_manager.need_step():
            self.step_manager.step()
            return

        # distance_set = distance()
        # distance_front = distance_set[2]
        # distance_front_left = distance_set[4]
        # distance_front_right = distance_set[0]
        # distance_rear_left = distance_set[3]
        # distance_rear_right = distance_set[1]

        distance_front = t.p.ranging.get(2)
        distance_front_left = t.p.ranging.get(4)
        distance_rear_left = t.p.ranging.get(3)

        lower_boundary = 180
        upper_boundary = 280
        error_distance = 10

        print '\033[1;36m{}\033[0m'.format('WALL FOLLOWING START')
        if 20 < distance_front < 300:
            l, r = [0, 0]
            self.done = True
        else:
            if distance_front_left > 5000 or distance_rear_left > 5000:
                l, r = [0, 0]
            else:
                if distance_front_left == 0 and 10 < distance_rear_left < upper_boundary:
                    l, r = [0.2, 0.9]
                elif distance_front_left == 0 and distance_rear_left > upper_boundary:
                    l, r = [0.1, 0.5]
                elif distance_front_left == 0 or distance_rear_left == 0:
                    l, r = [0, 0]
                else:
                        # case 1
                        if distance_front_left < lower_boundary and distance_rear_left < lower_boundary:
                            l, r = [0.5, 0.2]
                        # case 2
                        elif distance_front_left > upper_boundary and distance_rear_left > upper_boundary:
                            if distance_front_left > 900 and distance_rear_left > 900 and distance_front > 500:
                                l, r = [0.1, 0.9]

                                self.step_manager.add_n_times(
                                    setlr_closure(0.1, 0.9),
                                    times=duration2times(0.7)
                                )
                                self.step_manager.add_n_times(
                                    setlr_closure(0.3, 0.3),
                                    times=duration2times(0.4)
                                )

                            elif 500 < distance_front_left <= 900 or 500 < distance_rear_left <= 900:
                                self.step_manager.add_n_times(
                                    setlr_closure(0.2, 0.5),
                                    times=duration2times(0.2)
                                )
                                # st1 = time.time()
                                # while time.time() < st1 + 0.2:
                                #     l, r = [0.5, 0.2]
                                #     t.peripheral.wheels.set_lr(r, l)
                            else:
                                if (distance_rear_left - distance_front_left) < 20:
                                    self.step_manager.add_n_times(
                                        setlr_closure(0.2, 0.5),
                                        times=duration2times(0.2)
                                    )
                                    # st1 = time.time()
                                    # while time.time() < st1 + 0.2:
                                    #     l, r = [0.5, 0.1]
                                    #     t.peripheral.wheels.set_lr(r, l)
                                else:
                                    self.step_manager.add_n_times(
                                        setlr_closure(0.5, 0.2),
                                        times=duration2times(0.2)
                                    )

                        # case 3
                        elif distance_front_left < lower_boundary and distance_rear_left > lower_boundary:
                            l, r =[0.5, 0.2]
                        # case 4
                        elif distance_front_left > lower_boundary and distance_rear_left < lower_boundary:
                            if distance_front_left > 500 or distance_rear_left < 10:
                                l, r = [0.1, 0.5]
                            else:
                                self.step_manager.add_n_times(
                                    setlr_closure(0.4, 0.4),
                                    times=duration2times(0.3)
                                )
                                l, r = [0.1, 0.5]
                        # case 5
                        elif distance_front_left < upper_boundary and distance_rear_left > upper_boundary:
                            self.step_manager.add_n_times(
                                setlr_closure(0.4, 0.4),
                                times=duration2times(0.3)
                            )
                            l, r = [0.5, 0.2]
                        # case 6
                        elif distance_front_left > upper_boundary and distance_rear_left < upper_boundary:
                            l, r = [0.1, 0.6]
                        # case 7
                        else:
                            if distance_front_left < (distance_rear_left - error_distance) or distance_rear_left > (distance_front_left + error_distance):
                                l, r = [0.5, 0.2]
                            elif distance_front_left > (distance_rear_left+error_distance) or distance_rear_left < (distance_front_left-error_distance):
                                l, r = [0.2, 0.5]
                            else:
                                l, r = [0.4, 0.4]

        try:
            t.peripheral.wheels.set_lr(l, r)
        except UnboundLocalError:
            pass

        print '\033[1;36m{}\033[0m'.format('WALL FOLLOWING END')


if __name__ == '__main__':
    class TestTask(t.Task):
        def __init__(self):
            super(TestTask, self).__init__()
            self.task = PlanterWallFollower()

        def step(self):
            if not self.task.done:
                self.task.step()
            else:
                sys.exit()

    tttt = t.Tortoise()
    tttt.task = TestTask()
    tttt.walk()
