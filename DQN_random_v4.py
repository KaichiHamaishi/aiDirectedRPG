# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 15:24:29 2021

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
            l_input=L.Linear(input_count,50),
            l0=L.Linear(50,50),
            l1=L.Linear(50,50),
            l2=L.Linear(50,50),
            l3=L.Linear(50,50),
            l_output=L.Linear(50,output_count)

        )
        
    def __call__(self,x,y):
        return F.mean_squared_error(self.fwd(x), y)

    def fwd(self,x):
         h_input = F.relu(self.l_input(x))
         h0=F.relu(self.l0(h_input))
         h1=F.relu(self.l1(h0))
         h2=F.relu(self.l2(h1))
         h3=F.relu(self.l3(h2))
         h_output = self.l_output(h3)
         return h_output


class DQN_random_v4(director):
    description="DQN_random_v3改造、報酬の入力100回毎にのみ学習を行う"
    model=None
    x_len=0
    y_len=0
    x_training=[deque() for _ in range(100)]
    y_training=[deque() for _ in range(100)]
    scores=[0 for _ in range(100)]
    epsilon=1.0
    random=True
    
    learning_slot=0
    
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
        if(self.random):
            #最初のうちは完全ランダム
            result_index=random.choices(range(len(map_obj)),k=2)
        else:
            #前向き計算、ディレクションを取得
            xV=Variable(player_status)
            ans=self.model.fwd(xV).data[0]
            ans=ans-np.min(ans)
            #重み付きランダム
            result_index=random.choices(range(len(map_obj)),k=2,weights=ans)
        result_index=np.sort(result_index)
        result=map_obj[result_index]
        if random:
            #print("["+','.join(map(lambda t:t.name,result))+"]")
            pass
        #記録
        self.x_training[self.learning_slot].append(player_status)
        self.y_training[self.learning_slot].append(result_index)
        
        return result.tolist()
    def learn(self,reward):
        #重複の数だけ報酬減額
        dup=self.count_duplication(self.y_training[self.learning_slot])
        reward-=0.2*dup
        #報酬クリッピング
        if(reward<0):
            reward=-1.0
        self.scores[self.learning_slot]=reward
        self.learning_slot+=1
        
        if self.learning_slot>=100:
            self.learning_slot=0
            for j in range(100):
                #学習データを変形
                y_score=np.zeros((len(self.y_training[j]),self.y_len))
                for i in range(len(self.y_training[j])):
                    y_score[i][self.y_training[j][i]]=self.scores[j]
                x = Variable(np.array(self.x_training[j]))
                y = Variable(y_score.astype(np.float32))
                #学習
                self.model.zerograds()
                loss = self.model(x,y)
                loss.backward()
                self.optimizer.update()
            #ゴミ捨て
            for i in range(100):
                self.x_training[i].clear()
                self.y_training[i].clear()
            #完全ランダムにする可能性を変更
            if self.epsilon>0:
                self.epsilon-=0.01
            if self.epsilon<0:
                self.epsilon=0
            self.random=np.random.rand()<self.epsilon
            print("ε:"+str(self.epsilon)+","+str(self.random))
    def count_duplication(self,array):
        unique=deque()
        duplicate=0
        for i in array:
            if(not any(unique) or i in unique):
                duplicate+=1
            else:
                unique.append(i)
        return duplicate