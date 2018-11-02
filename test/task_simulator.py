# coding=utf-8

import multiprocessing
import time
import psutil
import uuid
import random
import string

def getCPURate():

    return psutil.cpu_percent(None)


def getMemRate():

    return psutil.virtual_memory().percent


def pvMonitor():
    pass

def worker(interval):
    n = 5
    while n > 0:
        print("The time is {0}".format(time.ctime()))
        time.sleep(interval)
        n -= 1

def cpuworker(targetRate = 70):

    interval = 0.003
    curr_num = 10001


    while True :
        # print("The time is {0}".format(time.ctime()))
        piworker(curr_num)
        rate = getCPURate()
        print rate
        # print getMemRate()


        # if rate < targetRate + 10 and (curr_num < curr_num * 10):
        #     curr_num += 1000
        # elif (rate > targetRate) and (curr_num > 1000):
        #     curr_num -= 1000
        # print "current pi length: %d" %(curr_num)

        while rate > (targetRate * 0.8) :
            # slp = interval * (100 - (rate - targetRate))
            slp = interval * (100 - targetRate)
            print "sleep %f to cool it down" %(slp)
            time.sleep(slp)
            rate = getCPURate()

def piworker(number = 10000):
    time1 = time.time()

    # 多计算10位，防止尾数取舍的影响
    number1 = number + 10

    # 算到小数点后number1位
    b = 10 ** number1

    # 求含4/5的首项
    x1 = b * 4 // 5
    # 求含1/239的首项
    x2 = b // -239

    # 求第一大项
    he = x1 + x2
    # 设置下面循环的终点，即共计算n项
    number *= 2

    # 循环初值=3，末值2n,步长=2
    for i in xrange(3, number, 2):
        # 求每个含1/5的项及符号
        x1 //= -25
        # 求每个含1/239的项及符号
        x2 //= -57121
        # 求两项之和
        x = (x1 + x2) // i
        # 求总和
        he += x

        # rate = getCPURate()
        # if rate > targetRate:
            # print "sleep to cool it down"
            # time.sleep(0.1)

    # 求出π
    pai = he * 4
    # 舍掉后十位
    pai //= 10 ** 10

    ############ 输出圆周率π的值
    paistring = str(pai)
    result = paistring[0] + str('.') + paistring[1:len(paistring)]
    # print result
    time2 = time.time()
    # print u'总共耗时：' + str(time2 - time1) + 's'


def memworker(targetRate = 70):

    rate = getMemRate()
    print rate

    data = {}

    while True:
        if rate < targetRate:
            data[str(uuid.uuid4())] = randstring()

        if (rate > targetRate) and len(data) > 0 :
            data.popitem()

        time.sleep(0.2)
        rate = getMemRate()
        print rate


def ioworker(targetRate = 100):

    rrate = int(targetRate * 0.8)
    wrate = targetRate - rrate

    while True:

        time1 = time.time()

        rtime = random.random()
        time.sleep(rtime)

        randfile = "/tmp/tmp_" + str(uuid.uuid4())

        for i in range(wrate):
            with open(randfile,"aw") as fh:
                fh.write(randstring(4*1024))

        for i in range(rrate):
            with open(randfile,"r") as fh:
                fh.read((4*1024))

        time2 = time.time()
        ltime = 1 - rtime - (time2 - time1)
        if ltime > 0.01 :
            time.sleep(ltime)


def randstring(size = 1024*1024):
    r = random.sample(string.ascii_letters + string.digits, 1)
    str  = r[0].zfill(size)
    return str

if __name__ == "__main__":
    # p = multiprocessing.Process(target = worker, args = (3,))
    # p.start()

    cpu_target = 80
    mem_target = 50
    io_target = 100

    cpus = psutil.cpu_count()
    for i in range(cpus):
        p = multiprocessing.Process(target=cpuworker, name="cpuworker_"  + str(i), args=(cpu_target,))
        p.start()
        print "p.pid:", p.pid
        print "p.name:", p.name
        print "p.is_alive:", p.is_alive()

    p = multiprocessing.Process(target=memworker, name="memworker" + "1", args=(mem_target,))
    p.start()
    print "p.pid:", p.pid
    print "p.name:", p.name
    print "p.is_alive:", p.is_alive()

    p = multiprocessing.Process(target=ioworker, name="ioworker" + "1", args=(io_target,))
    p.start()
    print "p.pid:", p.pid
    print "p.name:", p.name
    print "p.is_alive:", p.is_alive()