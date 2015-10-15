#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import random
import math

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]

# New York 的 LaGuardia 机场
destination = 'LGA'

flights = {}


# 读取航班信息
for line in file('schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])

    # 将航班信息详情添加到航班列表中
    flights[(origin, dest)].append((depart, arrive, int(price)))


# 计算某个给定时间在一天中的分钟数
def get_minutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]


# 打印时间表
def print_schedule(r):
    for d in range(len(r) / 2):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][r[2 * d]]
        ret = flights[(destination, origin)][r[2 * d + 1]]
        print '%10s%10s %5s-%5s $%3s %5s-%5s &%3s' % (name, origin,
                                                      out[0], out[1], out[2],
                                                      ret[0], ret[1], ret[2])


# 计算总的旅行成本
def schedule_cost(sol):
    total_price = 0
    latest_arrival = 0
    earliest_dep = 24 * 60

    for d in range(len(sol) / 2):
        # 得到往程航班和返程航班
        origin = people[d][1]
        out_bound = flights[(origin, destination)][int(sol[2 * d])]
        return_f = flights[(destination, origin)][int(sol[2 * d + 1])]

        # 总价格等于所有往程航班和返程航班价格之和
        total_price += out_bound[2]
        total_price += return_f[2]

        # 记录最晚到达时间和最早离开时间
        if latest_arrival < get_minutes(out_bound[1]):
            latest_arrival = get_minutes(out_bound[1])
        if earliest_dep > get_minutes(return_f[0]):
            earliest_dep = get_minutes(return_f[0])

        # 每个人必须在机场等待直到最后一个人到达为止
        # 他们也必须在相同时间到达，并等候他们的返程航班
        total_wait = 0
        for d in range(len(sol) / 2):
            origin = people[d][1]
            out_bound = flights[(origin, destination)][int(sol[2 * d])]
            return_f = flights[(destination, origin)][int(sol[2 * d + 1])]
            total_wait += latest_arrival - get_minutes(out_bound[1])
            total_wait += get_minutes(return_f[0]) - earliest_dep

        # 这个题解要求多租一天车费吗，如果是，则加上费用
        if latest_arrival < earliest_dep:
            total_price += 50

    return total_price + total_wait


# 随机搜索
# domain 是一个二元元组，它指定了每个变量的最大值和最小值
# costf 是成本函数，本例中 即 schedule_cost
def random_optimize(domain, costf):
    best = 999999999
    best_r = None
    # 随机产生1000次猜测，并对每一次猜测调用成本函数
    for i in range(1000):
        # 创建一个随机解
        r = [random.randint(domain[i][0], domain[i][1])
                for i in range(len(domain))]

        # 得到成本
        cost = costf(r)

        # 与到目前为止的最优解进行比较
        if cost < best:
            best = cost
            best_r = r
    return r


# 爬山法
def hill_climb(domain, costf):
    # 创建一个随机解
    sol = [random.randint(domain[i][0], domain[i][1])
            for i in range(len(domain))]

    # 主循环
    while 1:

        # 创建相邻解的列表
        neighbors = []

        for j in range(len(domain)):

            # 在每个方向上相对于原值偏离一点
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j+1:])

            if sol[j] < domain[j][1]:
                neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j+1:])

        # 在相邻解种寻找最优解
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]

        # 如果没有更好的解，则退出循环
        if best == current:
            break

    return sol


# 退火法
def annealing_optimize(domain, costf, T=10000.0, cool=0.95, step=1):
    # 随机初始化值
    vec = [float(random.randint(domain[i][0], domain[i][1]))
            for i in range(len(domain))]

    while T > 0.1:
        # 选择一个索引值
        i = random.randint(0, len(domain) - 1)

        # 选择一个改变索引值的方向
        dir = random.randint(-step, step)

        # 创建一个代表题解的新列表，改变其中一个值
        vec_b = vec[:]
        vec_b[i] += dir
        if vec_b[i] < domain[i][0]:
            vec_b[i] = domain[i][0]
        elif vec_b[i] > domain[i][1]:
            vec_b[i] = domain[i][1]

        # 计算当前成本和新的成本
        ea = costf(vec)
        eb = costf(vec_b)

        # 判断是否为更优解，或者时趋向最优解的可能临界解
        if (eb < ea or random.random() < pow(math.e, -(eb - ea) / T)):
            vec = vec_b

        # 降低温度
        T = T * cool

    return vec


if __name__ == '__main__':
    domain = [(0, 9)] * (len(people) * 2)

    print '----------random_optimize----------'

    t1 = time.time()
    s = random_optimize(domain, schedule_cost)
    print time.time() - t1
    print schedule_cost(s)
    print_schedule(s)

    print '----------hill_climb----------'

    t1 = time.time()
    s = hill_climb(domain, schedule_cost)
    print time.time() - t1
    print schedule_cost(s)
    print_schedule(s)

    print '----------annealing_optimize----------'

    t1 = time.time()
    s = annealing_optimize(domain, schedule_cost)
    print time.time() - t1
    print schedule_cost(s)
    print_schedule([int(x) for x in s])
