import time

import tortoise as t
import tool


class PourFishFoodTask(t.Task):
    def __init__(self):
        super(PourFishFoodTask, self).__init__()
        self.operations = iter([t.p.servo.mid, t.p.servo.max])

        self.sm = tool.StepManager()

        self.done = False

    def step(self):
        if self.sm.need_step():
            self.sm.step()
            return

        if tool.run_n_time_flag(self, 'uahishdfuiah', 2):
            self.operations.next()
        elif tool.run_n_time_flag(self, 'asdfa', 1):
            self.st_time = time.time()
            self.sm.add_blocking(
                lambda: None,
                lambda: time.time() - self.st_time < 5)
        else:
            self.done = True
