# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 14:55:31 2021

@author: Kaichi Hamaishi
"""

from director import director

import numpy as np
import chainer
from chainer import cuda, Function, gradient_check, Variable 
from chainer import optimizers, serializers, utils
from chainer import Link, Chain, ChainList
import chainer.functions as F
import chainer.links as L
from collections import deque


class DirectorChain(Chain):
    def __init__(self,input_count,output_count):
        super(DirectorChain, self).__init__(
            l1=L.Linear(input_count,10),
            l2=L.Linear(10,10),
            l3=L.Linear(10,output_count)

        )
        
    def __call__(self,x,y):
        return F.mean_squared_error(self.fwd(x), y)

    def fwd(self,x):
         h1 = F.sigmoid(self.l1(x))
         h2 = F.sigmoid(self.l2(h1))
         h3 = self.l3(h2)
         return h3


class DQN_director_v1(director):
    description="ディレクションを記録しておき、その記録と報酬を学習データにする。"
    model=None
    x_len=0
    y_len=0
    epsilon=1.0
    x_training=deque()
    y_training=deque() 
    
    def __init__(self):
        pass
    
    def make_map(self,floor,player,enemies,treasures):
        #引数を適切な形に変形
        map_obj=np.asarray(enemies+treasures)
        player_status=np.array([[floor]+player.status_array()]).astype(np.float32)
        #初期化されてないなら初期化
        if self.model is None:
            self.x_len=len(player_status[0])
            self.y_len=len(map_obj)
            self.model = DirectorChain(self.x_len,self.y_len)
            self.optimizer = optimizers.SGD()
            self.optimizer.setup(self.model)
        #イプシロンの確率でランダムに選ぶ、そうしないとすぐに収束してしまう
        if(np.random.rand()<self.epsilon):
            ans=np.random.rand(self.y_len)
        else:
            #前向き計算、ディレクションを取得
            xV=Variable(player_status)
            ans=self.model.fwd(xV).data[0]
        result_index=ans.argsort()[:-3:-1]
        result=map_obj[result_index]
        print("["+','.join(map(lambda t:t.name,result))+"]")
        #記録
        self.x_training.append(player_status)
        self.y_training.append(result_index)
        
        return result.tolist()
    def learn(self,reward):
        #学習データを変形
        y_score=np.zeros((len(self.y_training),self.y_len))
        for i in range(len(self.y_training)):
            y_score[i][self.y_training[i]]=reward
        x = Variable(np.array(self.x_training))
        y = Variable(y_score.astype(np.float32))
        #学習
        self.model.zerograds()
        loss = self.model(x,y)
        loss.backward()
        self.optimizer.update()
        #ゴミ捨て
        self.x_training.clear()
        self.y_training.clear()
        #ランダムに選ぶ可能性をへらす
        self.epsilon-=0.01