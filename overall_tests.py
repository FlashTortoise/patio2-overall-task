import time
from sys import argv

import tortoise as t


def yaw():
    while True:
        print t.p.yaw.get()
        time.sleep(0.2)


def inclination():
    inc = t.p.inclination

    class SimpleTask(t.Task):
        def __init__(self):
            super(SimpleTask, self).__init__()

        def step(self):
            print '{}, {}'.format(inc.pitch(), inc.roll())

    tttt = t.Tortoise()
    tttt.task = SimpleTask()
    tttt.walk()


def ranging():
    d = t.p.ranging
    while True:
        st = time.time()
        for i in range(5):
            print "%9.0f" % d.get(i),

        ed = time.time()
        print '   ', st - ed

        time.sleep(0.2)


def wheels():
    try:
        t.p.wheels.lr = 0.3, 0.3
        print 'should forward'
        raw_input('pause')
        t.p.wheels.lr = -0.3, 0.3
        print 'should left rotate'
        raw_input('pause')
        t.p.wheels.lr = 0.3, -0.3
        print 'should right rotate'
        raw_input('pause')
        t.p.wheels.lr = -0.3, -0.3
        print 'should backward'
        raw_input('pause')
    finally:
        t.p.wheels.lr = 0, 0


def servo():
    try:
        t.p.servo.min()
        print 'should at init angle'
        raw_input('pause')
        t.p.servo.mid()
        print 'should at mid angle'
        raw_input('pause')
        t.p.servo.max()
        print 'should at poured angle'
        raw_input('pause')
    finally:
        t.p.servo.min()


SENSOR_DEVICES = {
    'yaw': yaw,
    'inclination': inclination,
    'ranging': ranging
}

EFFECTOR_DEVICES = {
    'wheels': wheels,
    'servo': servo
}


def sensors():
    for name, tester in SENSOR_DEVICES.iteritems():
        print 'TEST {} START'.format(name.capitalize())
        try:
            tester()
        except KeyboardInterrupt:
            print 'TEST {} FINISHED'.format(name.capitalize())

        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            print 'INTERRUPTED'
            break


def effectors():
    for name, tester in EFFECTOR_DEVICES.iteritems():
        print 'TEST {} START'.format(name.capitalize())
        try:
            tester()
        except KeyboardInterrupt:
            pass
        print 'TEST {} FINISHED'.format(name.capitalize())

        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            print 'INTERRUPTED'
            break


def whole():
    sensors()
    effectors()


if __name__ == '__main__':
    try:
        test_item = argv[1]
    except IndexError:
        test_item = 'whole'

    {name: tester for name, tester in globals().iteritems() if name.islower()}[test_item]()
