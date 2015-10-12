# -*- coding:utf-8 -*-

from pysqlite2 import dbapi2 as sqlite
import nn

__author__ = 'Yrh'


# 搜索引擎搜索类
class Searcher(object):
    def __init__(self, db_name):
        # 建立数据库连接
        self.con = sqlite.connect(db_name)

    def __del__(self):
        # 关闭数据库连接
        self.con.close()

    # 获得匹配特定关键字的结果
    def get_match_rows(self, q):
        # 构造查询的字符串
        field_list = 'w0.urlid'
        table_list = ''
        clause_list = ''
        word_ids = []

        # 根据空格拆分单词
        words = q.split(' ')
        table_number = 0

        for word in words:
            # 获取单词的 ID
            word_row = self.con.execute("select rowid from wordlist where word='%s'" % word).fetchone()
            if word_row is not None:
                word_id = word_row[0]
                word_ids.append(word_id)
                if table_number > 0:
                    table_list += ','
                    clause_list += ' and '
                    clause_list += 'w%d.urlid=w%d.urlid and ' % (table_number - 1, table_number)
                field_list += ',w%d.location' % table_number
                table_list += 'wordlocation w%d' % table_number
                clause_list += 'w%d.wordid=%d' % (table_number, word_id)
                table_number += 1

        # 根据各个分组，建立查询
        full_query = 'select %s from %s where %s' % (field_list, table_list, clause_list)

        try:
            cur = self.con.execute(full_query)
        except:
            return None

        rows = [row for row in cur]

        return rows, word_ids

    #########################################################
    #################### 打 分 方 法 #########################
    #########################################################

    # 根据链接文本打分
    # word_ids：查询单词 id 列表
    def link_text_score(self, rows, word_ids):
        link_scores = dict([(row[0], 0) for row in rows])
        for word_id in word_ids:
            cur = self.con.execute(
                'select link.fromid, link.toid from linkwords, link where wordid=%d and linkwords.linkid=link.rowid' % word_id)
            for (from_id, to_id) in cur:
                if to_id in link_scores:
                    pr = self.con.execute('select score from pagerank where urlid=%d' % from_id).fetchone()[0]
                    link_scores[to_id] += pr
        max_score = max(link_scores.values())
        normalized_scores = dict([(u, float(l) / max_score) for (u, l) in link_scores.items()])
        return normalized_scores

    # 根据 PageRank 打分
    def page_rank_score(self, rows):
        # 得到 PageRank 数据
        page_ranks = dict(
            [(row[0], self.con.execute('select score from pagerank where urlid=%d' % row[0]).fetchone()[0])
             for row in rows])
        max_rank = max(page_ranks.values())
        normalized_scores = dict([(u, float(l) / max_rank) for (u, l) in page_ranks.items()])
        return normalized_scores

    # 根据回指链接打分
    def inbound_link_score(self, rows):
        unique_urls = set([row[0] for row in rows])
        inbound_count = dict(
            [(u, self.con.execute("select count(*) from link where toid=%d" % u).fetchone()[0]) for u in unique_urls])

        return self.normalizes_scores(inbound_count)

    # 根据关键词之间的距离打分
    def distance_score(self, rows):
        # 如果仅有一个单词、则得分都一样
        if len(rows[0]) <= 2:
            return dict([(rows[0], 1.0) for row in rows])

        # 初始化字典，并填入一个很大的数
        min_distance = dict([(row[0], 1000000) for row in rows])

        for row in rows:
            dist = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
            if dist < min_distance[row[0]]:
                min_distance[row[0]] = dist

        return self.normalizes_scores(min_distance, small_is_better=1)

    # 根据单词出现的位置打分
    def location_score(self, rows):
        locations = dict([(row[0], 1000000) for row in rows])
        for row in rows:
            loc = sum(row[1:])
            if loc < locations[row[0]]:
                locations[row[0]] = loc

        return self.normalizes_scores(locations, small_is_better=1)

    # 单词频度计算打分
    def frequency_score(self, rows):
        counts = dict([(row[0], 0) for row in rows])
        for row in rows:
            counts[row[0]] += 1

        return self.normalizes_scores(counts)

    # 获得查询结果评分
    def get_scored_list(self, rows, word_ids):
        total_scores = dict([(row[0], 0) for row in rows])

        # 此处是放置评价函数的地方
        weights = [(1.0, self.frequency_score(rows)), (1.0, self.location_score(rows)),
                   (1.0, self.page_rank_score(rows))]

        for (weight, scores) in weights:
            for url in total_scores:
                total_scores[url] += weight * scores[url]

        return total_scores

    # 获得 Url 地址
    def get_url_name(self, id):
        return self.con.execute("select url from urllist where rowid=%d" % id).fetchone()[0]

    # 对评价值进行归一化操作
    def normalizes_scores(self, scores, small_is_better=0):
        vs_mall = 0.00001  # 避免被 0 整除
        if small_is_better:
            min_score = min(scores.values())
            # 小值 / 大值 -> 值变小 | 小值 / 小值 -> 值变大
            return dict([(u, float(min_score) / max(vs_mall, l)) for (u, l) in scores.items()])
        else:
            max_score = max(scores.values())
            if max_score == 0:
                max_score = vs_mall
            return dict([(u, float(c) / max_score) for (u, c) in scores.items()])

    # 查询
    def query(self, q, page_number=10):

        if self.get_match_rows(q) is None:
            return False

        rows, word_ids = self.get_match_rows(q)

        scores = self.get_scored_list(rows, word_ids)
        ranked_scores = sorted([(score, url) for (url, score) in scores.items()], reverse=1)
        for (score, url_id) in ranked_scores[0:page_number]:
            print '%f\t%s' % (score, self.get_url_name(url_id))

        return word_ids, [r[1] for r in ranked_scores[0:10]]

    def nn_score(self, rows, word_ids):
        url_ids = [urlid for urlid in set([row[0] for row in rows])]
        my_net = nn.Searcher('nn.db')
        nn_res = my_net.get_result(word_ids, url_ids)
        scores = dict([(url_ids[i], nn_res[i]) for i in range(len(url_ids))])
        return self.normalizes_scores(scores)

if __name__ == '__main__':
    s = Searcher('searchindex.db')
    if not s.query('http', page_number=9):
        print 'Query Failed!'
