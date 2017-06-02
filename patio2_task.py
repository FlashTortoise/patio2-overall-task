import logging

import sys

import math

import tool
import tortoise as t

# noinspection PyUnresolvedReferences
from car_find_color import ColorTracingTask
from beacon_detect import BeaconDetectionTask
from turning import Turning
from wall_following_task_indoor import PlanterWallFollower

t.update_config(TORTOISE_WALK_PERIOD=0.1)
logging.getLogger('tortoise.p').setLevel(logging.WARN)
logging.getLogger('tortoise.main').setLevel(logging.WARN)


def duration2times(duration):
    return int(math.ceil(duration/float(t.config.TORTOISE_WALK_PERIOD)))


class Patio2(t.Task):
    logger = logging.getLogger('tortoise.patio2')

    def __init__(self):
        super(Patio2, self).__init__()

        self.color_block_tracing = ColorTracingTask()
        self.color_block_tracing.threshold_area = 120000
        self.b_2planter_task = BeaconDetectionTask()

        self.t_at_planter = Turning(-110)

        self.wall_following_task = PlanterWallFollower()

        self.t_before_feed_fish = Turning(-110)

        self.b_2fish_task = BeaconDetectionTask()
        self.b_2fish_task.direction_constant = 4
        self.b_2fish_task.threshold_area = 130000

        self.t_at_fish_food = Turning(-200)

        self.b_2communication_task = BeaconDetectionTask()
        self.b_2communication_task.threshold_area = 130000
        self.b_2communication_task.direction_constant = 4

        self.step_manager = tool.StepManager()

    def step(self):
        if self.step_manager.need_step():
            self.step_manager.step()
            return

        if False:
            pass
        elif not self.color_block_tracing.flag_cfc_end:
            print '\033[0;32m{}\033[0m'.format('Color block tracing')
            self.color_block_tracing.step()
        elif not self.b_2planter_task.done:
            print '\033[0;32m{}\033[0m'.format('Go to planner')
            self.b_2planter_task.step()
            print 'Area: {:9.1f}, direction: {:8s}'.format(
                self.b_2planter_task.beacon_area, self.b_2planter_task.turn_dir)

            self.set_speeds_from_beacon_flag(self.b_2planter_task.turn_dir)
        elif tool.run_n_time_flag(self, 'asdfaw'):
            print '\033[0;32m{}\033[0m'.format('Turning when hit planter')

            self.step_manager.add_blocking(
                self.t_at_planter.step,
                lambda: not self.t_at_planter.finish_flag
            )
        elif (
            tool.run_n_time_flag(self, 'faehiudcjr',time=duration2times(20))
            or not self.wall_following_task.done
        ):
            if tool.run_n_time_flag(self, 'faehiudcjr', peek=True):
                self.wall_following_task.done = False
            self.wall_following_task.step()
        elif tool.run_n_time_flag(self, 'asfawefoijwj'):
            print '\033[0;32m{}\033[0m'.format('Turning to fish food')
            self.step_manager.add_blocking(
                self.t_before_feed_fish.step,
                lambda: not self.t_before_feed_fish.finish_flag
            )

            def consume_photo():
                t.p.eye.see()
            self.step_manager.add_n_times(consume_photo, 10)

        elif not self.b_2fish_task.done:
            print '\033[0;32m{}\033[0m'.format('Go to feed fish')

            self.b_2fish_task.step()
            print 'Area: {:9.1f}, direction: {:8s}'.format(
                self.b_2fish_task.beacon_area, self.b_2fish_task.turn_dir)

            self.set_speeds_from_beacon_flag(self.b_2fish_task.turn_dir)
        elif tool.run_n_time_flag(self, 'yogokut'):
            print '\033[0;32m{}\033[0m'.format('Turning to communication')
            self.step_manager.add_blocking(
                self.t_at_fish_food.step,
                lambda: not self.t_at_fish_food.finish_flag
            )
        elif not self.b_2communication_task.done:
            print '\033[0;32m{}\033[0m'.format('Go to communication')
            self.b_2communication_task.step()
            print 'Area: {:9.1f}, direction: {:8s}'.format(
                self.b_2communication_task.beacon_area, self.b_2communication_task.turn_dir)

            self.set_speeds_from_beacon_flag(self.b_2communication_task.turn_dir)
        else:
            sys.exit()

    def set_speeds_from_beacon_flag(self, flag):
        if flag == 'right':
            t.p.wheels.lr = 0.4, 0.1
        elif flag == 'left':
            t.p.wheels.lr = 0.1, 0.4
        else:
            t.p.wheels.lr = 0.4, 0.4

if __name__ == '__main__':
    tttt = t.Tortoise()
    tttt.task = Patio2()
    tttt.walk()
