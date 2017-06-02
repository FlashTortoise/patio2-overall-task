from collections import deque

from tortoise import p, Task, Tortoise


class PIDController(object):
    def __init__(self, kp, ki, kd):
        self._kp, self._ki, self._kd = kp, ki, kd

        self._a0 = self._kp + self._ki + self._kd
        self._a1 = (- self._kp) - 2 * self._kd
        self._a2 = self._kd

        self.lx = 0
        self.llx = 0
        self.ly = 0

    def run(self, x):
        y = self.ly + self._a0 * x + self._a1 * self.lx + self._a2 * self.llx
        self.ly, self.lx, self.llx = y, x, self.lx
        return y

    @property
    def kp(self):
        return self._kp

    @property
    def ki(self):
        return self._ki

    @property
    def kd(self):
        return self._kd

    @kp.setter
    def kp(self, value):
        self._kp = value
        self._a0 = self._kp + self._ki + self._kd
        self._a1 = (- self._kp) - 2 * self._kd

    @ki.setter
    def ki(self, value):
        self._ki = value
        self._a0 = self._kp + self._ki + self._kd

    @kd.setter
    def kd(self, value):
        self._kd = value
        self._a0 = self._kp + self._ki + self._kd
        self._a1 = (- self._kp) - 2 * self._kd
        self._a2 = self._kd


def constrain(a, l, u):
    if a > u:
        return u
    elif a < l:
        return l
    else:
        return a


class Turning(Task):
    def __init__(self, wanted_degree, deque_length=6):
        super(Turning, self).__init__()
        self.c = PIDController(0.04, 0, 0)
        self.target_yaw = None
        self.want_degree = wanted_degree
        self.finish_flag = False
        self.tolerant_angle = 10

        self.past_diffs = deque(maxlen=deque_length)

    def step(self):
        print '\033[1;36m{}\033[0m'.format('TURNING START')

        if self.target_yaw is None:
            self.target_yaw = p.yaw.get() + self.want_degree

        deg = p.yaw.get()
        diff = constrain(self.c.run(self.target_yaw - deg), 0.4, -0.4)

        # print deg, diff
        p.wheels.set_diff(speed=0, diff=-diff)
        print 'deg: {:8f}  target yaw:{:8f}  '.format(self.target_yaw, deg),

        self.past_diffs.append(self.target_yaw-deg)
        average_diff = abs(sum(
            [angle for angle in self.past_diffs]
        ))/float(len(self.past_diffs))
        print 'avg: {}'.format(average_diff)
        self.finish_flag = average_diff < self.tolerant_angle

        print '\033[1;36m{}\033[0m'.format('TURNING END')

        return self.finish_flag

if __name__ == '__main__':
    tt = Tortoise()
    tt.task = Turning(90)
    tt.walk()
