import time

import tortoise as t
import tool


class PourFishFoodTask(t.Task):
    def __init__(self):
        super(PourFishFoodTask, self).__init__()
        t.p.servo.min()
        self.operations = [t.p.servo.mid, t.p.servo.max]
        self.operations_iter = iter(self.operations)

        self.sm = tool.StepManager()
        self.wait_for_sec = 5

        self.done = False

    def step(self):
        if self.sm.need_step():
            self.sm.step()
            return

        if tool.run_n_time_flag(self, 'uahishdfuiah', len(self.operations)):
            self.operations_iter.next()()
        elif tool.run_n_time_flag(self, 'asdfa', 1):
            self.st_time = time.time()
            self.sm.add_blocking(
                lambda: None,
                lambda: time.time() - self.st_time < self.wait_for_sec)
        else:
            self.done = True

if __name__ == '__main__':
    tttt = t.Tortoise()
    tttt.task = PourFishFoodTask()
    tttt.walk()
