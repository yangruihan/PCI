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


if __name__ == '__main__':
    s = [1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3]
    print_schedule(s)
    print schedule_cost(s)
