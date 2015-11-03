#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
import math
<<<<<<< HEAD

__author__ = 'yangruihan'

# 代表宿舍， 每个宿舍有两个可用的隔间
=======
from optimization import *

__author__ = 'yangruihan'


#  代表宿舍，每个宿舍有两个可用的隔间
>>>>>>> origin/master
dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']

# 代表学生及其首选和次选
prefers = [('Toby', ('Bacchus', 'Hercules')),
           ('Steve', ('Zeus', 'Pluto')),
           ('Andrea', ('Athena', 'Zeus')),
           ('Sarah', ('Zeus', 'Pluto')),
           ('Dave', ('Athena', 'Bacchus')),
           ('Jeff', ('Hercules', 'Pluto')),
           ('Fred', ('Pluto', 'Athena')),
           ('Suzie', ('Bacchus', 'Hercules')),
           ('Laura', ('Bacchus', 'Hercules')),
           ('Neil', ('Hercules', 'Athena'))]

<<<<<<< HEAD
# 搜索定义域约束 [(0, 9), (0, 8) ... (0, 1), (0, 0)]
do_main = [(0, (len(dorms) * 2) - i - 1) for i in range(len(dorms) * 2)]
=======
# 搜索的定义域必须满足的约束
do_main = [(0, (len(dorms) * 2) - i - 1) for i in range(0, len(dorms) * 2)]
>>>>>>> origin/master


# 打印题解
def print_solution(vec):
    slots = []
    # 为每个宿舍建两个槽
    for i in range(len(dorms)):
        slots += [i, i]

<<<<<<< HEAD
    print slots

=======
>>>>>>> origin/master
    # 遍历每一名学生的安置情况
    for i in range(len(vec)):
        x = int(vec[i])

        # 从剩余槽中选择
        dorm = dorms[slots[x]]
<<<<<<< HEAD
        # 输出学生及其被分配的宿舍
        print prefers[i][0], dorm
        # 删除该槽
        del slots[x]

        print slots
        

if __name__ == '__main__':
    vec = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    print_solution(vec)
=======

        # 输出学生及其被分配的宿舍
        print prefers[i][0], dorm

        # 删除该槽
        del slots[x]


# 成本函数
def dorm_cost(vec):
    cost = 0
    # 建立一个槽序列
    slots = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]

    # 遍历每一名学生
    for i in range(len(vec)):
        x = int(vec[i])
        dorm = dorms[slots[x]]
        prefer = prefers[i][1]
        # 首选成本值为0， 次选成本值为1，不在选择范围内成本值为2
        if prefer[0] == dorm:
            cost += 0
        elif prefer[1] == dorm:
            cost += 1
        else:
            cost += 2

        del slots[x]

    return cost


if __name__ == '__main__':
    s = random_optimize(do_main, dorm_cost)
    print dorm_cost(s)
    s = genetic_optimize(do_main, dorm_cost)
    print_solution(s)
>>>>>>> origin/master
