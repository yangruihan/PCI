# -*-coding:utf-8 -*-

from math import sqrt
from bicluster import BiCluster
from PIL import Image, ImageDraw
import random

__author__ = 'Yrh'


# 读取数据文件
def read_file(file_name):
    lines = [line for line in file(file_name)]

    # 第一行是列标题
    col_names = lines[0].strip().split('\t')[1:]
    row_names = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        row_names.append(p[0])
        data.append([float(x) for x in p[1:]])
    return row_names, col_names, data


# 利用皮尔森相关性求两个博客的相似度
def pearson(v1, v2):
    # 简单求和
    sum1 = sum(v1)
    sum2 = sum(v2)

    # 求平方和
    sum1_sq = sum([v ** 2 for v in v1])
    sum2_sq = sum([v ** 2 for v in v2])

    # 求乘积之和
    p_sum = sum([v1[i] * v2[i] for i in range(len(v1))])

    # 计算
    num = p_sum - (sum1 * sum2) / len(v1)
    den = sqrt((sum1_sq - sum1 ** 2 / len(v1)) * (sum2_sq - sum2 ** 2 / len(v1)))

    if den == 0:
        return 0

    # 为了实现两个相似度越大的元素之间的距离越小，这里实际上是 (1 - [Pearson Score])
    return 1.0 - num / den


# 利用谷本系数求两个元素的相似度
def tanimoto(v1, v2):
    c1, c2, shr = 0, 0, 0

    for i in range(len(v1)):
        if v1[i] != 0: c1 += 1  # 出现在 1 中
        if v2[i] != 0: c2 += 1  # 出现在 2 中
        if v1[i] != 0 and v2[i] != 0: shr += 1  # 同时出现在 1、2 中

    return 1.0 - (float(shr) / (c1 + c2 - shr))


# 构造分级聚类树，返回其根节点
def hcluster(rows, distance=pearson):
    distances = {}
    current_clust_id = -1

    # 最开始的聚类就是数据集中的行
    clust = [BiCluster(rows[i], id=i) for i in range(len(rows))]

    while len(clust) > 1:
        lowest_pair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)

        # 遍历每一个配对，寻找最小距离
        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                # 用 distance 来缓存距离的计算值
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)

                d = distances[clust[i].id, clust[j].id]

                if d < closest:
                    closest = d
                    lowest_pair = (i, j)

        # 计算两个聚类的平均值
        merge_vec = [(clust[lowest_pair[0]].vec[i] + clust[lowest_pair[1]].vec[i]) / 2.0 for i in
                     range(len(clust[0].vec))]

        # 建立新的聚类
        new_cluster = BiCluster(merge_vec, left=clust[lowest_pair[0]], right=clust[lowest_pair[1]], distance=closest,
                                id=current_clust_id)

        # 不在原始集合中的聚类，其id为负数
        current_clust_id -= 1
        del clust[lowest_pair[1]]
        del clust[lowest_pair[0]]
        clust.append(new_cluster)

    return clust[0]


# 打印聚类树
def print_clust(clust, labels=None, n=0):
    # 利用缩进来建立层级布局
    for i in range(n):
        print '  ',
    if clust.id < 0:
        # 负标记代表这是一个分支
        print '-'
    else:
        # 正标记代表这是一个叶节点
        if labels == None:
            print clust.id
        else:
            print labels[clust.id]

    # 现在开始打印右侧分支和左侧分支
    if clust.left != None:
        print_clust(clust.left, labels=labels, n=n + 1)
        print_clust(clust.right, labels=labels, n=n + 1)


# 获得聚类树状图的高度
def get_height(clust):
    if clust.left is None and clust.right is None:
        return 1
    else:
        return get_height(clust.left) + get_height(clust.right)


# 根据总误差值生成缩放因子
def get_depth(clust):
    # 一个叶节点的距离是 0.0
    if clust.left is None and clust.right is None:
        return 0
    # 一个枝节点的距离等于左右两侧分支中距离较大者
    # 加上该枝节点自身的距离
    return max(get_depth(clust.left), get_depth(clust.right)) + clust.distance


# 绘制树状图
def draw_dendrogram(clust, labels, jpeg='clusters.jpg'):
    # 高度和宽度
    h = get_height(clust) * 20  # 20 像素
    w = 1200
    depth = get_depth(clust)

    # 由于宽度是固定的，因此我们需要对距离值做相应的调整
    scaling = float(w - 150) / depth

    # 新建一个白色背景的图片
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h / 2, 10, h / 2), fill=(255, 0, 0))

    # 画第一个节点
    draw_node(draw, clust, 10, (h / 2), scaling, labels)
    img.save(jpeg, 'JPEG')


# 绘制节点
def draw_node(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = get_height(clust.left) * 20
        h2 = get_height(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2

        # 线的长度
        l1 = clust.distance * scaling
        # 聚类到其子节点的垂直线
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))

        # 连接左侧节点的水平线
        draw.line((x, top + h1 / 2, x + l1, top + h1 / 2), fill=(255, 0, 0))

        # 连接右侧节点的水平线
        draw.line((x, bottom - h2 / 2, x + l1, bottom - h2 / 2), fill=(255, 0, 0))

        # 调用函数绘制左右节点
        draw_node(draw, clust.left, x + l1, top + h1 / 2, scaling, labels)
        draw_node(draw, clust.right, x + l1, bottom - h2 / 2, scaling, labels)
    else:
        # 如果这是一个叶节点，则绘制节点的标签
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))


# 转置原矩阵
def rotate_matrix(data):
    new_data = []
    for i in range(len(data[0])):
        new_row = [data[j][i] for j in range(len(data))]
        new_data.append(new_row)
    return new_data


# K-均值聚类方法
def kcluster(rows, distance=pearson, k=4):
    # 确定每个点的最小值和最大值
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]

    # 随机创建 k 个中心点
    clusters = [
        [random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0] for i in range(len(rows[0]))] for j in range(k)]

    last_matches = None
    for t in range(100):
        print 'Iteration %d' % t
        best_matches = [[] for i in range(k)]

        # 在每一行中寻找距离最近的中心点
        for j in range(len(rows)):
            row = rows[j]
            best_match = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[best_match], row):
                    best_match = i
            best_matches[best_match].append(j)

        # 如果结果与上一次相同，则整个过程结束
        if best_matches == last_matches:
            break
        last_matches = best_matches

        # 把中心点移动到其所有成员的平均位置处
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(best_matches[i]) > 0:
                for rowid in best_matches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j] /= len(best_matches[i])
                clusters[i] = avgs

    return best_matches


# 计算二维坐标
def scale_down(data, distance=pearson, rate=0.01):
    n = len(data)

    # 每一对数据项之间的真实距离
    real_dist = [[distance(data[i], data[j]) for j in range(n)] for i in range(0, n)]

    outer_sum = 0.0

    # 随机初始化节点在二维空间中的起始位置
    loc = [[random.random(), random.random()] for i in range(n)]
    fake_dist = [[0.0 for j in range(n)] for i in range(n)]

    last_error = None
    for m in range(0, 1000):
        # 寻找投影后的距离
        for i in range(n):
            for j in range(n):
                fake_dist[i][j] = sqrt(sum([(loc[i][x] - loc[j][x]) ** 2 for x in range(len(loc[i]))]))

        # 移动节点
        grad = [[0.0, 0.0] for i in range(n)]

        total_error = 0
        for k in range(n):
            for j in range(n):
                if k == j: continue
                # 误差值等于目标距离与当前距离之间差值的百分比
                error_term = (fake_dist[j][k] - real_dist[j][k]) / real_dist[j][k]

                # 每一个节点都需要根据误差的多少，按比例移离或移向其他节点
                grad[k][0] += ((loc[k][0] - loc[j][0]) / fake_dist[j][k]) * error_term
                grad[k][1] += ((loc[k][1] - loc[j][1]) / fake_dist[j][k]) * error_term

                # 记录总的误差值
                total_error += abs(error_term)

        print total_error

        # 如果节点移动之后的情况变糟，则程序结束
        if last_error and last_error < total_error: break
        last_error = total_error

        # 根据 rate 参数与 grad 值相乘的结果，移动每一个节点
        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][1] -= rate * grad[k][1]

    return loc


# 绘制 2D 图像
def draw_2d(data, labels, jpeg='mds2d.jpg'):
    img = Image.new('RGB', (2000, 2000), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        draw.text((x, y), labels[i], (0, 0, 0))
    img.save(jpeg, 'JPEG')


if __name__ == '__main__':
    blognames, words, data = read_file('blogdata.txt')
    coords = scale_down(data)
    draw_2d(coords, blognames, jpeg='blogs2d.jpg')
