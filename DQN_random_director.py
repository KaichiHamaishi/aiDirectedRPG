# -*- coding: utf-8 -*-
"""
Created on Sat May  8 16:36:29 2021

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
import random


class DirectorChain(Chain):
    def __init__(self,input_count,output_count):
        super(DirectorChain, self).__init__(
            l1=L.Linear(input_count,10),
            l2=L.Linear(10,10),
            l3=L.Linear(10,10),
            l4=L.Linear(10,output_count)

        )
        
    def __call__(self,x,y):
        return F.mean_squared_error(self.fwd(x), y)

    def fwd(self,x):
         h1 = F.relu(self.l1(x))
         h2 = F.relu(self.l2(h1))
         h3 = F.relu(self.l2(h2))
         h4 = self.l4(h3)
         return h4


class DQN_random_director(director):
    description="DQN_director_v3を、ε-グリーディから重み付きランダムに変更"
    model=None
    x_len=0
    y_len=0
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
            self.x_len=len(player_status[0]+2)
            self.y_len=len(map_obj)
            self.model = DirectorChain(self.x_len,self.y_len)
            self.optimizer = optimizers.SGD()
            self.optimizer.setup(self.model)
        #前向き計算、ディレクションを取得
        xV=Variable(player_status)
        ans=self.model.fwd(xV).data[0]
        #重み付きランダム
        result_index=random.choices(range(len(map_obj)),k=2,weights=ans)
        result_index=np.sort(result_index)
        result=map_obj[result_index]
        print("["+','.join(map(lambda t:t.name,result))+"]")
        #記録
        self.x_training.append(player_status)
        self.y_training.append(result_index)
        
        return result.tolist()
    def learn(self,reward):
        #重複の数だけ報酬減額
        dup=self.count_duplication(self.y_training)
        reward-=0.2*dup
        #報酬クリッピング
        if(reward<0.9):
            reward=-1.0
        else:
            reward=1.0
        
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
    def count_duplication(self,array):
        unique=deque()
        duplicate=0
        for i in array:
            if(not any(unique) or i in unique):
                duplicate+=1
            else:
                unique.append(i)
        return duplicate