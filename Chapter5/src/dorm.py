#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
import math

__author__ = 'yangruihan'

# 代表宿舍， 每个宿舍有两个可用的隔间
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

# 搜索定义域约束 [(0, 9), (0, 8) ... (0, 1), (0, 0)]
do_main = [(0, (len(dorms) * 2) - i - 1) for i in range(len(dorms) * 2)]


# 打印题解
def print_solution(vec):
    slots = []
    # 为每个宿舍建两个槽
    for i in range(len(dorms)):
        slots += [i, i]

    print slots

    # 遍历每一名学生的安置情况
    for i in range(len(vec)):
        x = int(vec[i])

        # 从剩余槽中选择
        dorm = dorms[slots[x]]
        # 输出学生及其被分配的宿舍
        print prefers[i][0], dorm
        # 删除该槽
        del slots[x]

        print slots
        

if __name__ == '__main__':
    vec = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    print_solution(vec)
