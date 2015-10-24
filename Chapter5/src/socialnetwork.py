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


# ���㽻���ߵĸ���
def cross_count(v):
    # ����������ת����һ�� person:(x, y) ���ֵ�
    loc = dict([(people[i], (v[i * 2], v[i * 2 + 1])) for i in range(0, len(people))])

    total = 0
    # ����ÿһ������
    for i in range(len(links)):
        for j in range(i + 1, len(links)):

            # ��ȡ����λ��
            (x1, y1), (x2, y2) = loc[links[i][0]], loc[links[i][1]]
            (x3, y3), (x4, y4) = loc[links[j][0]], loc[links[j][1]]

            # �ж������Ƿ񽻲棬��� den ����0~1֮�䣬�����߽��棬��֮���򲻽���
            den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

            # �������ƽ�У��� den == 0
            if den == 0:
                continue

            ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
            ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den

            # ��������ߵķ���ֵ���� 0~1 ֮�䣬�����߱˴˽���
            if ua > 0 and ua < 1 and ub > 0 and ub < 1:
                total += 1

        for i in range(len(people)):
            for j in range(i + 1, len(people)):
                # ���������λ��
                (x1, y1), (x2, y2) = loc[people[i]], loc[people[j]]

                # ���������ļ��
                dist = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

                # �Լ��С��50�����صĽڵ�����з�
                if dist < 50:
                    total += (1.0 - (dist / 50.0))

    return total


# ��������
def draw_network(sol):
    # ���� Image ����
    img = Image.new('RGB', (400, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # ������ʾλ����Ϣ���ֵ�
    pos = dict([(people[i], (sol[i * 2], sol[i * 2 + 1])) for i in range(0, len(people))])

    # ��������
    for (a, b) in links:
        draw.line((pos[a], pos[b]), fill=(255, 0, 0))

    # ���ƴ����˵Ľ��
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
