# -*- coding:utf-8 -*-

import requests
from BeautifulSoup import *
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'Yrh'

ignore_words = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


# 搜索引擎爬虫类
class Crawler(object):
    # 初始化 crawler 类并传入数据库名称
    def __init__(self, db_name):
        self.con = sqlite.connect(db_name)

    def __del__(self):
        self.con.close()

    def db_commit(self):
        self.con.commit()

    # 辅助函数，用于获得条目的 id ，并且如果条目不存在，就将其加入数据库中
    def get_entry_id(self, table, field, value, create_new=True):
        cur = self.con.execute("select rowid from %s where %s='%s'" % (table, field, value))
        res = cur.fetchone()
        if res is None:
            cur = self.con.execute("insert into %s(%s) values ('%s')" % (table, field, value))
            return cur.lastrowid
        else:
            return res[0]

    # 为每个网页建立索引
    def add_to_index(self, url, soup):
        if self.is_indexed(url):
            return
        print 'Indexing ' + url

        # 获取每一个单词
        text = self.get_text_only(soup)
        words = self.separate_words(text)

        # 得到 URL 的 id
        url_id = self.get_entry_id('urllist', 'url', url)

        # 将每个单词与该 url 关联
        for i in range(len(words)):
            word = words[i]
            # 如果单词在被忽略列表中，则继续下一轮循环
            if word in ignore_words:
                continue
            word_id = self.get_entry_id('wordlist', 'word', word)
            self.con.execute(
                'insert into wordlocation(urlid, wordid, location) values (%d, %d, %d)' % (url_id, word_id, i))

    # 从一个 HTML 网页中提取文字（不带标签的）
    def get_text_only(self, soup):
        v = soup.string
        if v is None:
            c = soup.contents
            result_text = ''
            for t in c:
                sub_text = self.get_text_only(t)
                result_text += sub_text + '\n'
            return result_text
        else:
            return v.strip()

    # 根据任何非空白字符进行分词处理
    def separate_words(self, text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s != '']

    # 如果 url 已经建过索引，则返回 true
    def is_indexed(self, url):
        u = self.con.execute("select rowid from urllist where url ='%s'" % url).fetchone()
        if u is not None:
            # 检查它是否已经被检索过了
            v = self.con.execute("select * from wordlocation where urlid=%d" % u[0]).fetchone()
            if v is not None:
                return True
        return False

    # 添加一个关联两个网站的链接
    def add_link_ref(self, url_from, url_to, link_text):
        words=self.separate_words(link_text)
        from_id=self.get_entry_id('urllist','url',url_from)
        to_id=self.get_entry_id('urllist','url',url_to)

        if from_id == to_id:
            return

        cur = self.con.execute("insert into link(fromid, toid) values (%d, %d)" % (from_id, to_id))
        link_id = cur.lastrowid
        for word in words:
            if word in ignore_words:
                continue
            word_id=self.get_entry_id('wordlist','word',word)
            self.con.execute("insert into linkwords(linkid, wordid) values (%d,%d)" % (link_id,word_id))

    # 从一小组网页开始进行广度优先搜索，直至某一给定深度
    # 期间为网页建立索引
    def crawl(self, pages, depth=2):
        for i in range(depth):
            new_pages = set()
            for page in pages:
                try:
                    c = requests.get(page)
                except:
                    print 'Could not open %s' % page
                    continue
                soup = BeautifulSoup(c.content)
                self.add_to_index(page, soup)

                links = soup('a')
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]  # 去掉位置部分
                        if url[0:4] == 'http' and not self.is_indexed(url):
                            new_pages.add(url)
                        link_text = self.get_text_only(link)
                        self.add_link_ref(page, url, link_text)

                self.db_commit()
            pages = new_pages

    # 计算每一个网页的PageRank值
    def calculate_page_rank(self, iterations=20):
        # 清除当前的 PageRank 表
        self.con.execute('drop table if exists pagerank')
        self.con.execute('create table pagerank(urlid primary key, score)')

        # 初始化每一个 url，令其 PageRank值为1
        self.con.execute('insert into pagerank select rowid, 1.0 from urllist')
        self.db_commit()

        # 迭代次数
        for i in range(iterations):
            print 'Iteration %d' % i
            for (url_id, ) in self.con.execute('select rowid from urllist'):
                # 最小值
                pr = 0.15

                # 循环遍历指向当前网页的所有其他网页
                for (linker, ) in self.con.execute('select distinct fromid from link where toid=%d' % url_id):
                    # 得到链接源对应网页的PageRank值
                    linking_pr = self.con.execute('select score from pagerank where urlid=%d' % linker).fetchone()[0]

                    # 根据链接源，求得总的链接数
                    linking_count = self.con.execute('select count(*) from link where fromid=%d' % linker).fetchone()[0]

                    pr += 0.85 * (linking_pr / linking_count)

                self.con.execute('update pagerank set score=%f where urlid=%d' % (pr, url_id))
            self.db_commit()

    # 创建数据库表
    def create_index_tables(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid, wordid, location)')
        self.con.execute('create table link(fromid integer, toid integer)')
        self.con.execute('create table linkwords(wordid, linkid)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.db_commit()


if __name__ == '__main__':
    page_list = ['http://kiwitobes.com/wiki/Categorical_list_of_programming_languages.html']
    page_list = ['https://github.com/yangruihan']
    crawler = Crawler('searchindex.db')
    crawler.create_index_tables()
    crawler.crawl(page_list, 2)
    crawler.calculate_page_rank()