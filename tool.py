from collections import deque
from itertools import repeat
from more_itertools import peekable


def run_n_time_flag(self, distinct_name, time=1, peek=False):
    """
    >>> class Something(object):
    ...     def hello(self):
    ...         print '#'*10,
    ...         if run_n_time_flag(self, 'one',time=5):
    ...             print 'executed',
    ...         print 'something'

    >>> s = Something()

    >>> for i in range(20):
    ...     s.hello()

    """
    if getattr(self, '_execute_record', None) is None:
        setattr(self, '_execute_record', {})

    rec = getattr(self, '_execute_record')

    if rec.get(distinct_name, None) is None:
        rec[distinct_name] = time

    if rec[distinct_name] > 0:
        if peek is False:
            rec[distinct_name] -= 1
        return True
    else:
        return False


class StepManager(object):
    def __init__(self):
        self.tasks = deque()

    def need_step(self):
        while True:
            try:
                task_info = self.tasks[0]
            except IndexError:
                return False

            try:
                p = task_info['need_iter'].peek()
            except StopIteration:
                p = False

            if p is False:
                self.tasks.popleft()
            else:
                return True

    def add_n_times(self, step, times):
        if not callable(step):
            raise Exception('task is not callable')

        self.tasks.append(dict(
            callable=step,
            need_iter=peekable(repeat(True, times))
        ))

    def add(self, step):
        self.add_n_times(step, times=1)

    def add_blocking(self, step, until):
        self.tasks.append(dict(
            callable=step,
            need_iter=peekable(iter(until, None))
        ))

    def step(self):
        need_iter = self.tasks[0]['need_iter'].next()
        task = self.tasks[0]['callable']
        if not need_iter:
            self.tasks.popleft()

        return task()


if __name__ == '__main__':
    class TestStepManager(object):
        def __init__(self):
            self.stepm = StepManager()
            self.executed_count = 0

        def step(self):
            if self.stepm.need_step():
                self.stepm.step()
                return

            print 'raw running'
            if self.executed_count == 3:
                def other_fun():
                    print 'other fun run'
                self.stepm.add_n_times(other_fun, 1)

                def another_fun():
                    print 'another fun run'
                self.stepm.add_n_times(another_fun, 2)

                def another_another_fun():
                    print 'another '*2 + 'fun run'
                it = repeat(True, 2)
                self.stepm.add_blocking(another_another_fun, it.next)

            self.executed_count += 1

    t = TestStepManager()
    for i in range(10):
        t.step()


