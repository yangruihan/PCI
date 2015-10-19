#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import urllib2
import xml.dom.minidom

__author__ = 'yangruihan'

kayak_key = 'YOUR KEY HERE'


def get_kayak_session():
    # 构造 URL 以开启一个会话
    url = 'http://www.kayak.com/k/ident/apisession?token=%s&version=1' % kayak_key

    # 解析返回的 XML
    doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

    # 找到 <sid>xxxxxxx</sid> 标签
    sid = doc.getElementsByTagName('sid')[0].firstChild.data

    return sid


def flight_search(sid, origin, destination, depart_date):
    # 构造搜索用的 URL
    url = 'http://www.kayak.com/s/apisearch?basicmode=true&oneway=y&origin=%s' % origin
    url += '&destination=%s&depart_date=%s' % (destination, depart_date)
    url += '&travelers=1&cabin=e&action=doFlights&apimode=1'
    url += '&_sid_=%s&version=1' % sid

    # 得到 XML
    doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

    # 提取搜索用的 ID
    search_id = doc.getElementsByTagName('searchid')[0].firstChild.data

    return search_id


def flight_search_results(sid, searchid):
    # 删除开头的$和逗号，并把数字转化成浮点类型
    def parse_price(p):
        return float(p[1:].replace(',', ''))

    # 遍历检测
    while 1:
        time.sleep(2)

        # 构造检测所用的 URL
        url = 'http://www.kayak.com/s/basic/flight?'
        url += 'searchid=%s&c=5&apimode=1&_sid_=%s&version=1' % (searchid, sid)
        doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

        # 寻找 morepending 标签，并等待其不再为 true
        more_pending = doc.getElementsByTagName('morepending')[0].firstChild
        if more_pending is None or more_pending.data == 'false':
            break

    # 现在，下载完整列表
    url = 'http://www.kayak.com/s/basic/flight?'
    url += 'searchid=%s&c=999&apimode=1&_sid_=%s&version=1' % (searchid, sid)
    doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())

    # 得到不同元素组成的列表
    prices = doc.getElementsByTagName('price')
    departures = doc.getElementsByTagName('depart')
    arrivals = doc.getElementsByTagName('arrive')

    # 用 zip 将它们连在一起
    return zip([p.firstChild.data.split(' ')[1] for p in departures],
               [p.firstChild.data.split(' ')[1] for p in arrivals],
               [parse_price(p.firstChild.data) for p in prices])


def create_schedule(people, dest, dep, ret):
    # 得到搜索用的会话 id
    sid = get_kayak_session()
    flights = {}

    for p in people:
        name, origin = p
        # 往程航班
        search_id = flight_search(sid, origin, dest, dep)
        flights[(origin, dest)] = flight_search_results(sid, search_id)

        # 返程航班
        search_id = flight_search(sid, dest, origin, ret)
        flights[(dest, origin)] = flight_search_results(sid, search_id)

    return flights
