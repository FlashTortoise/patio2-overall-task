import time

import tortoise as t
import tool

member_names = [
    'Wang Yuting', 'Xiong Mengkai', 'Jiang Hao', 'Cheng Di', 'Xie Zixuan',
    'Chen Yanhong', 'Luo Zhidan', 'Li Ruochen', 'Wen Yisi', 'Cheng Xiang']

def what_to_say():
    words = []

    words.append('TEAM MEMBERS:\r\n')

    max_name_len = max([len(n) for n in member_names])
    for i, n in enumerate(member_names):
        words.append(n.ljust(max_name_len + 4))
        if i % 2:
            words.append('\r\n')

    words.append('The Time now is:\r\n')
    words.append(time.asctime())
    words.append('\r\n')

    return ''.join(words)


class CommunicationTask(t.Task):
    def __init__(self):
        super(CommunicationTask, self).__init__()

        self.sm = tool.StepManager()
        self.done = False

    def step(self):
        if self.sm.need_step():
            self.sm.step()
            return

        if tool.run_n_time_flag(self, 'lol', 1):
            t.p.rxtx.send(what_to_say())
        elif self.done == False:
            recv = t.p.rxtx.recv()
            if recv != '':
                self.done = True
                print 'done'

if __name__ == '__main__':
    print what_to_say()

    tttt = t.Tortoise()
    tttt.task = CommunicationTask()
    tttt.walk()
