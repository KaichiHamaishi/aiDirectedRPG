# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 20:34:20 2021

@author: kaich
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
        with chainer.using_config('debug', True):
            h_input = F.sigmoid(self.l_input(x))
            h0=F.sigmoid(self.l0(h_input))
            h1=F.sigmoid(self.l1(h0))
            h2=F.sigmoid(self.l2(h1))
            h3=F.sigmoid(self.l3(h2))
            h_output = self.l_output(h3)
        return h_output


class rand_enemy_DQN_v2(director):
    description="階層だけを入力値として見る。"
    model=None
    x_len=0 #入力層(プレイヤーのステータス+現在位置)の長さ
    y_len=0 #出力層の長さ
    x_training=[deque() for _ in range(10)] #入力値。プレイヤーのステータス
    y_training=[deque() for _ in range(10)] #出した最終ディレクション
    y_law_training=[deque() for _ in range(10)] #ディレクションするにあたって使ったナマの値
    
    model_enemy_gen=None
    en_y_len=0 #出力層の長さ
    en_y_training=[deque() for _ in range(10)] #出した最終ディレクション
    en_y_law_training=[deque() for _ in range(10)] #ディレクションするにあたって使ったナマの値
    
    actual_result=[0 for _ in range(10)] #そのプレイでのプレイヤー最終到達階層
    epsilon=1.0
    random=True
    
    learning_slot=0
    
    def __init__(self):
        pass
    
    def make_map(self,floor,player,enemies,treasures):
        #引数を適切な形に変形
        map_obj=np.asarray(treasures)
        player_status=np.array([[floor]]).astype(np.float32)
        #初期化されてないなら初期化
        if self.model is None:
            self.x_len=len(player_status[0])
            self.y_len=len(map_obj)
            self.model = DirectorChain(self.x_len,self.y_len)
            self.optimizer = optimizers.SGD()
            self.optimizer.setup(self.model)
        if self.model_enemy_gen is None:
            self.en_y_len=1
            self.model_enemy_gen = DirectorChain(self.x_len,self.en_y_len)
            self.en_optimizer = optimizers.SGD()
            self.en_optimizer.lr=0.001
            self.en_optimizer.setup(self.model_enemy_gen)
            
            for _ in range(100):
                self.model_enemy_gen.zerograds()
                loss_en = self.model_enemy_gen((np.ones(100, dtype=np.float32)*5).reshape(100,1),(np.ones(100, dtype=np.float32)*4).reshape(100,1))
                loss_en.backward()
                self.en_optimizer.update()
        #前向き計算、ディレクションを取得
        xV=Variable(player_status)
        ans=self.model.fwd(xV).data[0]
        ans_en=self.model_enemy_gen.fwd(xV).data[0]
        #記録
        self.y_law_training[self.learning_slot].append(ans)
        self.en_y_law_training[self.learning_slot].append(ans_en)
        #最低値が0になるように加算
        ans_map=ans-np.min(ans)
        if(self.random):
            #完全ランダム
            result_index=random.choices(range(len(map_obj)),k=1)
            strength=random.random()*10.0
        else:
            #重み付きランダム
            result_index=random.choices(range(len(map_obj)),k=1,weights=ans_map)
            strength=round(ans_en[0])
            #プレビュー。ぜんぶだと見にくいから一回だけ
            if self.learning_slot==0:
                print(str(np.around(ans,2)))
                print(str(ans_en))
        result_index=np.sort(result_index)[0]
        #敵生成
        enemy_gen=enemy("モンスター Lv"+str(strength),round(strength*strength/2),strength,strength,[0.6,0.2,0.2],1,True)
        #最終結果
        result=[enemy_gen,map_obj[result_index]]
        #print("["+','.join(map(lambda t:t.name,result))+"]")
        #記録
        self.x_training[self.learning_slot].append(player_status)
        self.y_training[self.learning_slot].append(result_index)
        
        return result
    
    def learn(self,target,actual):
        #報酬の入力が一定回数あるまでは学習せずに報酬を記録
        self.actual_result[self.learning_slot]=actual
        self.learning_slot+=1
        
        #報酬の入力が溜まったらぜんぶ学習
        if self.learning_slot>=10:
            self.learning_slot=0
            
            for j in range(10):
                score=abs(target-self.actual_result[j])*-1.0
                #学習データを成形
                y_score=np.array(self.y_law_training[j].copy())
                en_y_score=np.array(self.en_y_law_training[j].copy())
                for i in range(len(self.y_training[j])):
                    y_score[i][self.y_training[j][i]]=score
                    if(i<=(self.actual_result[j])):
                        #en_sc=max(1,en_y_score[i][0]+(1 if(target-self.actual_result[j])<0 else -1))
                        en_sc=max(1,abs(en_y_score[i][0])-(target-self.actual_result[j]))
                        print("["+str(j)+"]["+str(i)+"]:"+str(en_sc))
                        en_y_score[i][0]=en_sc
                x = Variable(np.array(self.x_training[j]))
                y = Variable(y_score.astype(np.float32))
                y_en=Variable(en_y_score.astype(np.float32))
                #学習
                self.model.zerograds()
                loss = self.model(x,y)
                loss.backward()
                self.optimizer.update()
                self.model_enemy_gen.zerograds()
                loss_en = self.model_enemy_gen(x,y_en)
                loss_en.backward()
                self.en_optimizer.update()
                
                #いらなくなったデータを捨てる
                self.x_training[j].clear()
                self.y_training[j].clear()
                self.y_law_training[j].clear()
                self.en_y_training[j].clear()
                self.en_y_law_training[j].clear()
            
            
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