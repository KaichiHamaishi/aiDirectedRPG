# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 14:39:17 2021

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
import copy

from enemy import enemy


class DirectorChain(Chain):
    def __init__(self,input_count,output_count):
        super(DirectorChain, self).__init__(
            l_input=L.Linear(input_count,10),
            l0=L.Linear(10,10),
            l1=L.Linear(10,10),
            l2=L.Linear(10,10),
            l3=L.Linear(10,10),
            l_output=L.Linear(10,output_count)

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


class multiply_enemy_DQN(director):
    description="未完成 宝物とモンスターが従来通りの出方をする"
    model=None
    x_len=0
    y_len=0
    x_training=[deque() for _ in range(10)]
    y_training=[deque() for _ in range(10)]
    y_law_training=[deque() for _ in range(10)]
    scores=[0 for _ in range(10)]
    epsilon=1.0
    random=True
    
    str_model=None
    str_y_len=0 #出力層の長さ
    str_y_training=[deque() for _ in range(10)] #出した最終ディレクション
    str_y_law_training=[deque() for _ in range(10)] #ディレクションするにあたって使ったナマの値
    
    learning_slot=0
    
    def __init__(self):
        pass
    
    def make_map(self,floor,player,enemies,treasures):
        #引数を適切な形に変形
        silent=enemies[0].silent
        enemies=np.asarray([
            enemy("スライム",4,1,1,[0.5,0.5,0],1,silent),
            enemy("ゴブリン",3,2,1,[0.6,0.2,0.2],1,silent),
            enemy("ドラゴン",50,8,3,[0.6,0.1,0.3],3,silent)
            ])
        map_obj=np.asarray(enemies+treasures)
        player_status_randomized=np.array(list(map(self.seed_random,[floor]+player.status_array())))
        player_status=np.array([player_status_randomized]).astype(np.float32)
        #初期化されてないなら初期化
        if self.model is None:
            self.x_len=len(player_status[0])
            self.y_len=len(map_obj)
            self.model = DirectorChain(self.x_len,self.y_len)
            self.optimizer = optimizers.SGD()
            self.optimizer.setup(self.model)
        if self.str_model is None:
            self.str_y_len=1
            self.str_model = DirectorChain(self.x_len,self.str_y_len)
            self.str_optimizer = optimizers.SGD()
            #self.str_optimizer.lr=0.001
            self.str_optimizer.setup(self.str_model)
        #前向き計算、ディレクションを取得
        xV=Variable(player_status)
        ans=self.model.fwd(xV).data[0]
        ans_str=self.str_model.fwd(xV).data[0]
        #記録
        self.y_law_training[self.learning_slot].append(ans)
        #最低値が0になるように加算
        ans=ans-np.min(ans)
        if(self.random):
            #完全ランダム
            result_index=random.choices(range(len(map_obj)),k=2)
            strength=random.random()*10.0
        else:
            #重み付きランダム
            result_index=random.choices(range(len(map_obj)),k=2,weights=ans)
            strength=ans_str[0]
            if self.learning_slot==0:
                print(str(np.around(ans,2))+"->"+str(np.sort(result_index)))
        result_index=np.sort(result_index)
        #最終結果
        result=map_obj[result_index]
        #print("["+','.join(map(lambda t:t.name,result))+"]")
        #記録
        self.x_training[self.learning_slot].append(player_status)
        self.y_training[self.learning_slot].append(result_index)
        
        return result.tolist()
    
    def learn(self,reward):
        #重複の数だけ報酬減額
        #dup=self.count_duplication(self.y_training[self.learning_slot])
        #reward-=0.2*dup
        
        #報酬クリッピング
        #if(reward<0):
        #    reward=-1.0
        #if(reward>0):
        #    reward=1.0
        
        #報酬の入力が一定回数あるまでは学習せずに報酬を記録
        self.scores[self.learning_slot]=reward
        self.learning_slot+=1
        
        #報酬の入力が溜まったらぜんぶ学習
        if self.learning_slot>=10:
            self.learning_slot=0
            avg=abs(np.average(np.array(self.scores)))
            if avg<5:
                self.optimizer.lr=0.01/(10**((5-avg)/2))
            else:
                self.optimizer.lr=0.01
            for j in range(10):
                #学習データを成形
                y_score=np.array(self.y_law_training[j].copy())
                for i in range(len(self.y_training[j])):
                    y_score[i][self.y_training[j][i]]=self.scores[j]
                x = Variable(np.array(self.x_training[j]))
                y = Variable(y_score.astype(np.float32))
                #学習
                self.model.zerograds()
                loss = self.model(x,y)
                loss.backward()
                self.optimizer.update()
                
                #いらなくなったデータを捨てる
                self.x_training[j].clear()
                self.y_training[j].clear()
                self.y_law_training[j].clear()
            
            
            #完全ランダムにする可能性を変更
            if self.epsilon>0:
                self.epsilon-=0.05
            if self.epsilon<0:
                self.epsilon=0
            self.random=np.random.rand()<self.epsilon
            print("ε:"+str(self.epsilon)+","+str(self.random))
        
        #learnメソッドおわり
            
    #重複を数える関数
    def count_duplication(self,array):
        unique=deque()
        duplicate=0
        for i in array:
            if(not any(unique) or i in unique):
                duplicate+=1
            else:
                unique.append(i)
        return duplicate
    #シード値から乱数を求める関数
    def seed_random(self,seed):
        random.seed(seed)
        a=random.uniform(-10.0,10.0)
        random.seed(None)
        return a