#!/usr/bin/env python
# -*- coding:utf-8 -*-

import math
from optimization import *
from PIL import Image, ImageDraw 

__author__ = 'yrh'


people = ['Charlie', 'Augustus', 'Veruca', 'Violet', 'Mike', 'Joe', 'Willy', 'Miranda']

links = [('Augustus', 'Willy'),
         ('Mike', 'Joe'),
         ('Miranda', 'Mike'),
         ('Violet', 'Augustus'),
         ('Miranda', 'Willy'),
         ('Charlie', 'Mike'),
         ('Veruca', 'Joe'),
         ('Miranda', 'Augustus'),
         ('Willy', 'Augustus'),
         ('Joe', 'Charlie'),
         ('Veruca', 'Augustus'),
         ('Miranda', 'Joe')]


# 计算交叉线的个数
def cross_count(v):
    # 将数字序列转换成一个 person:(x, y) 的字典
    loc = dict([(people[i], (v[i * 2], v[i * 2 + 1])) for i in range(0, len(people))])

    total = 0
    # 遍历每一对连线
    for i in range(len(links)):
        for j in range(i + 1, len(links)):

            # 获取坐标位置
            (x1, y1), (x2, y2) = loc[links[i][0]], loc[links[i][1]]
            (x3, y3), (x4, y4) = loc[links[j][0]], loc[links[j][1]]

            # 判断两线是否交叉，如果 den 介于0~1之间，则两线交叉，反之，则不交叉
            den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

            # 如果两线平行，则 den == 0
            if den == 0:
                continue

            ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
            ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den

            # 如果两条线的分数值介于 0~1 之间，则两线彼此交叉
            if ua > 0 and ua < 1 and ub > 0 and ub < 1:
                total += 1

        for i in range(len(people)):
            for j in range(i + 1, len(people)):
                # 获得两结点的位置
                (x1, y1), (x2, y2) = loc[people[i]], loc[people[j]]

                # 计算两结点的间距
                dist = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

                # 对间距小于50个像素的节点进行判罚
                if dist < 50:
                    total += (1.0 - (dist / 50.0))

    return total


# 绘制网络
def draw_network(sol):
    # 建立 Image 对象
    img = Image.new('RGB', (400, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 建立标示位置信息的字典
    pos = dict([(people[i], (sol[i * 2], sol[i * 2 + 1])) for i in range(0, len(people))])

    # 绘制连线
    for (a, b) in links:
        draw.line((pos[a], pos[b]), fill=(255, 0, 0))

    # 绘制代表人的结点
    for n, p  in pos.items():
        draw.text(p, n, (0, 0, 0))

    img.show()


if __name__ == '__main__':
    do_main = [(10, 370)] * (len(people) * 2)
    print do_main
    sol = random_optimize(do_main, cross_count)
    print cross_count(sol)
    print sol
    draw_network(sol)
    sol = annealing_optimize(do_main, cross_count, step=50, cool=0.99)
    print cross_count(sol)
    print sol
    draw_network(sol)
