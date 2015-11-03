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
# cost_f 是成本函数，本例中 即 schedule_cost
def random_optimize(do_main, cost_f):
    best = 999999999
    best_r = None
    # 随机产生1000次猜测，并对每一次猜测调用成本函数
    for i in range(1000):
        # 创建一个随机解
        r = [random.randint(do_main[i][0], do_main[i][1])
             for i in range(len(do_main))]

        # 得到成本
        cost = cost_f(r)

        # 与到目前为止的最优解进行比较
        if cost < best:
            best = cost
            best_r = r
    return best_r


# 爬山法
def hill_climb(do_main, cost_f):
    # 创建一个随机解
    sol = []
    for i in range(len(do_main)):
        sol.append(random.randint(do_main[i][0], do_main[i][1]))

    # 主循环
    while 1:

        # 创建相邻解的列表
        neighbors = []

        for j in range(len(do_main)):

            # 在每个方向上相对于原值偏离一点
            if sol[j] > do_main[j][0]:
                neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j + 1:])

            if sol[j] < do_main[j][1]:
                neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j + 1:])

        # 在相邻解种寻找最优解
        current = cost_f(sol)
        best = current
        for j in range(len(neighbors)):
            cost = cost_f(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]

        # 如果没有更好的解，则退出循环
        if best == current:
            break

    return sol


# 退火法
def annealing_optimize(do_main, cost_f, t=10000.0, cool=0.95, step=1):
    # 随机初始化值
    vec = [float(random.randint(do_main[i][0], do_main[i][1]))
           for i in range(len(do_main))]

    while t > 0.1:
        # 选择一个索引值
        i = random.randint(0, len(do_main) - 1)

        # 选择一个改变索引值的方向
        dir = random.randint(-step, step)

        # 创建一个代表题解的新列表，改变其中一个值
        vec_b = vec[:]
        vec_b[i] += dir
        if vec_b[i] < do_main[i][0]:
            vec_b[i] = do_main[i][0]
        elif vec_b[i] > do_main[i][1]:
            vec_b[i] = do_main[i][1]

        # 计算当前成本和新的成本
        ea = cost_f(vec)
        eb = cost_f(vec_b)

        # 判断是否为更优解，或者时趋向最优解的可能临界解
        if eb < ea or random.random() < pow(math.e, -(eb - ea) / t):
            vec = vec_b

        # 降低温度
        t *= cool

    return vec


# 遗传算法
# 参数：
#       pop_size    种群大小
#       mut_prob    种群的新成员是由变异而非交叉得来的概率
#       elite       种群中被认为是优解且被允许传入下一代的部分
#       max_iter    须运行多少代
def genetic_optimize(do_main, cost_f, pop_size=50, step=1, mut_prob=0.2, elite=0.2, max_iter=100):
    # 变异操作
    def mutate(vec):
        i = random.randint(0, len(do_main) - 1)
        if random.random() < 0.5 and vec[i] > do_main[i][0]:
            return vec[0:i] + [vec[i] - step] + vec[i + 1:]
        elif vec[i] < do_main[i][1]:
            return vec[0:i] + [vec[i] + step] + vec[i + 1:]

    # 交叉操作
    def crossover(r1, r2):
        # 因为两个数组进行交叉，每一个数组最少要拿出一个元素，因此这里的上界是len(do_main)-2
        i = random.randint(1, len(do_main) - 2)
        return r1[0:i] + r2[i:]

    # 构造初始种群
    pop = []
    for i in range(pop_size):
        vec = [random.randint(do_main[i][0], do_main[i][1]) for i in range(len(do_main))]
        pop += [vec]

    # 每一代中有多少胜出者
    top_elite = int(elite * pop_size)

    # 主循环
    for i in range(max_iter):
        scores = []
        for v in pop:
            if v is None:
                continue
            scores.append((cost_f(v), v))
        # 对得分进行排序
        scores.sort()
        ranked = [v for (_, v) in scores]

        # 从纯粹的胜出者开始
        pop = ranked[0:top_elite]

        # 添加变异和配对后的胜出者
        while len(pop) < pop_size:
            if random.random() < mut_prob:
                # 变异
                c = random.randint(0, top_elite)
                pop.append(mutate(ranked[c]))
            else:
                # 交叉
                c1 = random.randint(0, top_elite)
                c2 = random.randint(0, top_elite)
                pop.append(crossover(ranked[c1], ranked[c2]))

        # 打印当前最优质
        # print scores[0][0]

    return scores[0][1]


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

    print '----------genetic_optimize----------'

    t1 = time.time()
    s = genetic_optimize(domain, schedule_cost)
    print time.time() - t1
    print schedule_cost(s)
    print_schedule(s)
