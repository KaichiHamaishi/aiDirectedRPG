# -*- coding: utf-8 -*-
"""
Created on Fri May 28 16:20:38 2021

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
    def __init__(self,input_count,output_count,middle_height,middle_width):
        self.middle_width=middle_width
        super(DirectorChain, self).__init__(
            l_first=L.Linear(input_count,middle_height),
            **{'middle_'+str(i) : L.Linear(middle_height,middle_height) for i in range(middle_width)},
            l_last=L.Linear(middle_height,output_count)

        )
        
    def __call__(self,x,y):
        return F.mean_squared_error(self.fwd(x), y)

    def fwd(self,x):
         h_first = F.relu(self.l_first(x))
         h_mid=h_first
         for i in range(self.middle_width):
             h_mid=F.relu(globals()["middle_"+str(i)](h_mid))
         h_last = self.l_last(h_first)
         return h_last


class DQN_random_v2(director):
    description="DQN_random_directorの、中間層の数を可変に(未完成)"
    model=None
    x_len=0
    y_len=0
    x_training=deque()
    y_training=deque() 
    epsilon=1.0
    random=True
    
    def __init__(self,middle_height=10,middle_width=2):
        self.middle_height=middle_height
        self.middle_width=middle_width
        pass
    
    def make_map(self,floor,player,enemies,treasures):
        #引数を適切な形に変形
        map_obj=np.asarray(enemies+treasures)
        player_status=np.array([[floor]+player.status_array()]).astype(np.float32)
        #初期化されてないなら初期化
        if self.model is None:
            self.x_len=len(player_status[0]+2)
            self.y_len=len(map_obj)
            self.model = DirectorChain(self.x_len,self.y_len,self.middle_height,self.middle_width)
            self.optimizer = optimizers.SGD()
            self.optimizer.setup(self.model)
        if(self.random):
            #最初のうちは完全ランダム
            result_index=random.choices(range(len(map_obj)),k=2)
        else:
            #前向き計算、ディレクションを取得
            xV=Variable(player_status)
            ans=self.model.fwd(xV).data[0]
            #重み付きランダム
            result_index=random.choices(range(len(map_obj)),k=2,weights=ans)
        result_index=np.sort(result_index)
        result=map_obj[result_index]
        #print("["+','.join(map(lambda t:t.name,result))+"]")
        #記録
        self.x_training.append(player_status)
        self.y_training.append(result_index)
        
        return result.tolist()
    def learn(self,reward):
        #重複の数だけ報酬減額
        dup=self.count_duplication(self.y_training)
        reward-=0.2*dup
        #報酬クリッピング
        if(reward<0.5):
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
        #完全ランダムにする可能性を変更
        if reward>0 or self.random:
            if(self.epsilon>0):
                self.epsilon-=0.1
        elif(self.epsilon<1.0):
            self.epsilon+=0.1
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