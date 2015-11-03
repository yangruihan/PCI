#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import math

__author__ = 'yangruihan'


def sample_train(c1):
    c1.train('Nobody owns the water', 'good')
    c1.train('the quick rabbit jumps fences', 'good')
    c1.train('buy pharmaceuticals now', 'bad')
    c1.train('make quick money at the online casino', 'bad')
    c1.train('the quick brown fox jumps', 'good')


def get_words(doc):
    splitter = re.compile('\\W*')
    
    # 根据非字母字符进行单词划分
    words = [s.lower() for s in splitter.split(doc) if len(s) > 2 and len(s) < 20]

    # 只返回一组不重复的单词
    return dict([w, 1] for w in words)


# 分类器
class classifier(object):
    def __init__(self, get_features, filename=None):
        # 统计特征/分类组合的数量
        self.fc = {}
        # 统计每个分类中的文档数量
        self.cc = {}
        # 得到特征的函数
        self.get_features = get_features

    # 增加对特征/分类组合的计数值
    def inc_f(self, f, cat):
        self.fc.setdefault(f, {})
        self.fc[f].setdefault(cat, 0)
        self.fc[f][cat] += 1

    # 增加对某一分类的计数器
    def inc_c(self, cat):
        self.cc.setdefault(cat, 0)
        self.cc[cat] += 1

    # 某一特征出现于某一分类中的次数
    def f_count(self, f, cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0

    # 属于某一分类的内容项数量
    def cat_count(self, cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0.0

    # 所有内容项的数量
    def total_count(self):
        return sum(self.cc.values())

    # 所有分类的列表
    def categories(self):
        return self.cc.keys()

    # 训练
    def train(self, item, cat):
        features = self.get_features(item)
        # 针对该分类的每个特征增加计数器
        for f in features:
            self.inc_f(f, cat)

        # 增加针对该分类的计数值
        self.inc_c(cat)


if __name__ == '__main__':
    c1 = classifier(get_words)
    c1.train('the quick brown fox jumps over the lazy dog', 'good')
    c1.train('make quick money in the online casino', 'bad')
    print c1.f_count('quick', 'good')
    print c1.f_count('quick', 'bad')
