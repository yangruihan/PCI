# -*- coding:utf-8 -*-

import feedparser
import re

__author__ = 'Yrh'


def get_words(html):
    # 去除所有 HTML 标记
    txt = re.compile(r'<[^>]+>').sub('', html)

    # 利用所有非字母字符拆分出单词
    words = re.compile(r'[^A-Z^a-z]+').split(txt)

    # 转化成小写形式
    return [word.lower() for word in words if word != '']


# 返回一个RSS订阅源的标题和包含单词计数情况的字典
def get_word_counts(url):
    # 解析订阅源
    d = feedparser.parse(url)
    wc = {}

    # 循环遍历所有的文章条目
    for e in d.entries:
        if 'summary' in e:
            summary = e.summary
        else:
            summary = e.description

        # 提取一个单词列表
        words = get_words(e.title + ' ' + summary)
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1
    return d.feed.title, wc


if __name__ == '__main__':
    ap_count = {}
    word_counts = {}
    feed_list = [line for line in file('feedlist.txt')]
    for feed_url in feed_list:
        try:
            title, wc = get_word_counts(feed_url)
            word_counts[title] = wc
            for word, count in wc.items():
                ap_count.setdefault(word, 0)
                if count > 1:
                    ap_count[word] += 1
        except:
            print 'Failed to parse feed %s' % feed_url

    word_list = []
    for w, bc in ap_count.items():
        frac = float(bc) / len(feed_list)
        if 0.1 < frac < 0.5:
            word_list.append(w)

    out = file('blogdata.txt', 'w')
    out.write('Blog')
    for word in word_list:
        out.write('\t%s' % word)
    out.write('\n')
    for blog, wc in word_counts.items():
        print blog
        out.write(blog)
        for word in word_list:
            if word in wc:
                out.write('\t%d' % wc[word])
            else:
                out.write('\t0')
        out.write('\n')

    print 'Finished!'
