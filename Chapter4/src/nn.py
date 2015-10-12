# -*-coding:utf-8-*-

from math import tanh
from pysqlite2 import dbapi2 as sqlite

__author__ = 'Yrh'


# return the slope of tanh
def dtanh(y):
    return 1.0 - y * y


class Searchnet:
    def __init__(self, db_name):
        self.con = sqlite.connect(db_name)

    def __del__ (self):
        self.con.close()

    # create database tables
    def make_tables(self):
        self.con.execute('create table hiddennode(create_key)')
        self.con.execute('create table wordhidden(fromid, toid, strength)')
        self.con.execute('create table hiddenurl(fromid, toid, strength)')
        self.con.commit()

    # return the strength of linking
    def get_strength(self, from_id, to_id, layer):
        table = self.get_layer(layer)

        # get the strength from table
        res = self.con.execute('select strength from %s where fromid=%d and toid=%d' \
            % (table, from_id, to_id)).fetchone()

        if res is None:
            # the default value of word layer - hidden layer is -0.2
            if layer == 0:
                return -0.2
            # the defalut value of hidden layer - url layer is 0
            if layer == 1:
                return 0
        return res[0]

    def set_strength(self, from_id,to_id, layer, strength):
        table = self.get_layer(layer)

        res = self.con.execute('select rowid from %s where fromid=%d and toid=%d' \
            % (table, from_id, to_id)).fetchone()
        # if strength not exists, create it
        if res is None:
            self.con.execute('insert into %s (fromid, toid, strength) values (%d, %d, %f)' \
                % (table, from_id, to_id, strength))
        else:  # if strength exists, update it
            rowid = res[0]
            self.con.execute('update %s set strength =%f where rowid=%d' % \
                (table, strength, rowid))

    # generate hidden node when a new combination of words
    def generate_hidden_node(self, word_ids, urls):
        if len(word_ids) > 3:
            return None

        # check the node has existed
        create_key = '_'.join(sorted([str(wi) for wi in word_ids]))
        res = self.con.execute("select rowid from hiddennode where create_key='%s'" \
            % create_key).fetchone()

        # if not exist
        if res is None:
            cur = self.con.execute("insert into hiddennode (create_key) values ('%s')"\
                % create_key)
            hidden_id = cur.lastrowid
            # set default weight
            for word_id in word_ids:
                self.set_strength(word_id, hidden_id, 0, 1.0 / len(word_ids))
            for url_id in urls:
                self.set_strength(hidden_id, url_id, 1, 0.1)
            self.con.commit()

    def get_layer(self, layer_id):
        # layer == 0 -> word layer - hidden layer
        if layer_id == 0:
            return 'wordhidden'
        else:
            return 'hiddenurl'

    # return all relate hidden id
    def get_all_hidden_ids(self, word_ids, url_ids):
        l1 = {}
        for word_id in word_ids:
            cur = self.con.execute('select toid from wordhidden where fromid=%d' % word_id)
            for row in cur:
                l1[row[0]] = 1
        for url_id in url_ids:
            cur = self.con.execute('select fromid from hiddenurl where toid=%d' % url_id)
            for row in cur:
                l1[row[0]] = 1
        return l1.keys()

    # set up the network
    def set_up_network(self, word_ids, url_ids):
        # value table
        self.word_ids = word_ids
        self.hidden_ids = self.get_all_hidden_ids(word_ids, url_ids)
        self.url_ids = url_ids

        # node output
        self.ai = [1.0] * len(self.word_ids)
        self.ah = [1.0] * len(self.hidden_ids)
        self.ao = [1.0] * len(self.url_ids)

        # build the weight matrix
        self.wi = [[self.get_strength(word_id, hidden_id, 0)
                    for hidden_id in self.hidden_ids]
                    for word_id in self.word_ids]
        self.wo = [[self.get_strength(hidden_id, url_id, 1)
                    for url_id in self.url_ids]
                    for hidden_id in self.hidden_ids]

    def feed_forward(self):
        # query word that is the only input
        for i in range(len(self.word_ids)):
            self.ai[i] = 1.0

        # active level of hidden node
        for j in range(len(self.hidden_ids)):
            sum = 0.0
            for i in range(len(self.word_ids)):
                sum += self.ai[i] * self.wi[i][j]
            self.ah[j] = tanh(sum)

        # active level of output node
        for k in range(len(self.url_ids)):
            sum = 0.0
            for j in range(len(self.hidden_ids)):
                sum += self.ah[j] * self.wo[j][k]
            self.ao[k] = tanh(sum)

        return self.ao[:]

    # build the network
    def get_result(self, word_ids, url_ids):
        self.set_up_network(word_ids, url_ids)
        return self.feed_forward()

    def back_propagate(self, targets, N=0.5):
        # calculate output layer error
        output_deltas = [0.0] * len(self.url_ids)
        for k in range(len(self.url_ids)):
            error = targets[k] - self.ao[k]
            output_deltas[k] = dtanh(self.ao[k]) * error

        # calculate hidden layer error
        hidden_deltas = [0.0] * len(self.hidden_ids)
        for j in range(len(self.hidden_ids)):
            error = 0.0
            for k in range(len(self.url_ids)):
                error += output_deltas[k] * self.wo[j][k]
            hidden_deltas[j] = dtanh(self.ah[j]) * error

        # update output weight
        for j in range(len(self.hidden_ids)):
            for k in range(len(self.url_ids)):
                change = output_deltas[k] * self.ah[j]
                self.wo[j][k] += N * change

        # update input weight
        for i in range(len(self.word_ids)):
            for j in range(len(self.hidden_ids)):
                change = hidden_deltas[j] * self.ai[i]
                self.wi[i][j] += N * change

    def train_query(self, word_ids, url_ids, selected_url):
        # if neccessary, generate a hidden node
        self.generate_hidden_node(word_ids, url_ids)

        self.set_up_network(word_ids, url_ids)
        self.feed_forward()

        targets = [0.0] * len(url_ids)
        targets[url_ids.index(selected_url)] = 1.0

        self.back_propagate(targets)
        self.update_database()

    def update_database(self):
        # put value into database
        for i in range(len(self.word_ids)):
            for j in range(len(self.hidden_ids)):
                self.set_strength(self.word_ids[i], self.hidden_ids[j], 0, self.wi[i][j])

        for j in range(len(self.hidden_ids)):
            for k in range(len(self.url_ids)):
                self.set_strength(self.hidden_ids[j], self.url_ids[k], 1, self.wo[j][k])
        self.con.commit()


if __name__ == '__main__':
    my_net = Searchnet('nn.db')
    # my_net.make_tables()
    w_world, w_river, w_bank = 101, 102, 103
    u_world_bank, u_river, u_earth = 201, 202, 203
    my_net.train_query([w_world, w_bank], [u_world_bank, u_river, u_earth], u_world_bank)
    print my_net.get_result([w_world, w_bank], [u_world_bank, u_river, u_earth])

