# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 18:03:40 2021

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
        with chainer.using_config('debug', True):
            h_input = F.relu(self.l_input(x))
            h0=F.relu(self.l0(h_input))
            h1=F.relu(self.l1(h0))
            h2=F.relu(self.l2(h1))
            h3=F.relu(self.l3(h2))
            h_output = self.l_output(h3)
        return h_output


class multiply_enemy_DQN(director):
    description="難易度を学習し、モンスターの能力値を難易度だけ倍にする。"
    
    x_training=[deque() for _ in range(10)] #入力値。プレイヤーのステータス
    x_len=0 #入力層(プレイヤーのステータス+現在位置)の長さ
    
    treasure_model=None
    treasure_y_len=0 #出力層の長さ
    treasure_y_training=[deque() for _ in range(10)] #出した最終ディレクション
    treasure_y_law_training=[deque() for _ in range(10)] #ディレクションするにあたって使ったナマの値
    
    enemy_model=None
    enemy_y_len=0 #出力層の長さ
    enemy_y_training=[deque() for _ in range(10)] #出した最終ディレクション
    enemy_y_law_training=[deque() for _ in range(10)] #ディレクションするにあたって使ったナマの値
    
    str_model=None
    str_y_len=0 #出力層の長さ
    str_y_training=[deque() for _ in range(10)] #出した最終ディレクション
    str_y_law_training=[deque() for _ in range(10)] #ディレクションするにあたって使ったナマの値
    
    actual_result=[0 for _ in range(10)] #そのプレイでのプレイヤー最終到達階層
    epsilon=1.0
    random=True
    
    learning_slot=0
    
    def __init__(self):
        pass
    
    def make_map(self,floor,player,enemies,treasures):
        #引数を適切な形に変形
        trej_obj=np.asarray(treasures)
        silent=enemies[0].silent
        enemy_obj=np.asarray([
            enemy("スライム",4,1,2,[0.5,0.5,0],1,silent),
            enemy("ゴブリン",3,2,1,[0.6,0.2,0.2],1,silent),
            enemy("ドラゴン",4,2,2,[0.6,0.1,0.3],3,silent)
            ])
        #player_status=np.array([[floor]]).astype(np.float32)
        player_status=np.array([[floor]+player.status_array()]).astype(np.float32)
        #初期化されてないなら初期化
        if self.treasure_model is None:
            self.x_len=len(player_status[0])
            self.treasure_y_len=len(trej_obj)
            self.treasure_model = DirectorChain(self.x_len,self.treasure_y_len)
            self.treasure_optimizer = optimizers.SGD()
            self.treasure_optimizer.setup(self.treasure_model)
        if self.enemy_model is None:
            self.enemy_y_len=len(enemy_obj)
            self.enemy_model = DirectorChain(self.x_len,self.enemy_y_len)
            self.enemy_optimizer = optimizers.SGD()
            self.enemy_optimizer.setup(self.enemy_model)
        if self.str_model is None:
            self.str_y_len=1
            self.str_model = DirectorChain(self.x_len,self.str_y_len)
            self.str_optimizer = optimizers.SGD()
            #self.str_optimizer.lr=0.001
            self.str_optimizer.setup(self.str_model)
            
        #前向き計算、ディレクションを取得
        xV=Variable(player_status)
        ans_trej=self.treasure_model.fwd(xV).data[0]
        ans_enemy=self.enemy_model.fwd(xV).data[0]
        ans_str=self.str_model.fwd(xV).data[0]
        #記録
        self.treasure_y_law_training[self.learning_slot].append(ans_trej)
        self.enemy_y_law_training[self.learning_slot].append(ans_enemy)
        self.str_y_law_training[self.learning_slot].append(ans_str)
        #最低値が0になるように加算
        ans_trej=ans_trej-np.min(ans_trej)
        ans_enemy=ans_enemy-np.min(ans_enemy)
        if(self.random):
            #完全ランダム
            treasure_result_index=random.choices(range(len(trej_obj)),k=1)
            enemy_result_index=random.choices(range(len(enemy_obj)),k=1)
            strength=random.random()*10.0
        else:
            """
            ##重み付きランダム
            treasure_result_index=random.choices(range(len(trej_obj)),k=1,weights=ans_trej)
            enemy_result_index=random.choices(range(len(enemy_obj)),k=1,weights=ans_enemy)
            strength=ans_str[0]
            """
            treasure_result_index=ans_trej.argsort()[::-1]
            enemy_result_index=ans_enemy.argsort()[::-1]
            strength=ans_str[0]
            #プレビュー。ぜんぶだと見にくいから一回だけ
            if self.learning_slot==0:
                print(str(np.around(ans_trej,2)))
                print(str(np.around(ans_enemy,2)))
                print(str(ans_str))
        #敵生成
        base_enemy=enemy_obj[enemy_result_index[0]]
        enemy_gen=enemy(
            base_enemy.name+" Lv"+str(round(strength,2)),
            base_enemy.hp*strength,
            base_enemy.attack*strength,
            base_enemy.shield*strength,
            base_enemy.chances,
            base_enemy.exp,
            base_enemy.silent
            )
        #最終結果
        result=[enemy_gen,trej_obj[np.sort(treasure_result_index)[0]]]
        #print("["+','.join(map(lambda t:t.name,result))+"]")
        #記録
        self.x_training[self.learning_slot].append(player_status)
        self.treasure_y_training[self.learning_slot].append(np.sort(treasure_result_index)[0])
        self.enemy_y_training[self.learning_slot].append(np.sort(enemy_result_index)[0])
        
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
                treasure_y_score=np.array(self.treasure_y_law_training[j].copy())
                enemy_y_score=np.array(self.enemy_y_law_training[j].copy())
                str_y_score=np.array(self.str_y_law_training[j].copy())
                for i in range(len(self.treasure_y_training[j])):
                    treasure_y_score[i][self.treasure_y_training[j][i]]=score
                    enemy_y_score[i][self.enemy_y_training[j][i]]=score
                    if(i<=(self.actual_result[j])):
                        #str_sc=max(1,str_y_score[i][0]+(1 if(target-self.actual_result[j])<0 else -1))
                        str_sc=max(1,abs(str_y_score[i][0])-(target-self.actual_result[j]))
                        print("["+str(j)+"]["+str(i)+"]:"+str(str_sc))
                        str_y_score[i][0]=str_sc
                x = Variable(np.array(self.x_training[j]))
                y_treasure = Variable(treasure_y_score.astype(np.float32))
                y_enemy = Variable(enemy_y_score.astype(np.float32))
                y_strength=Variable(str_y_score.astype(np.float32))
                #学習
                self.treasure_model.zerograds()
                loss = self.treasure_model(x,y_treasure)
                loss.backward()
                self.treasure_optimizer.update()
                
                self.enemy_model.zerograds()
                enemy_loss = self.enemy_model(x,y_enemy)
                enemy_loss.backward()
                self.enemy_optimizer.update()
                
                self.str_model.zerograds()
                str_loss = self.str_model(x,y_strength)
                str_loss.backward()
                self.str_optimizer.update()
                
                #いらなくなったデータを捨てる
                self.x_training[j].clear()
                self.treasure_y_training[j].clear()
                self.treasure_y_law_training[j].clear()
                self.enemy_y_training[j].clear()
                self.enemy_y_law_training[j].clear()
                self.str_y_training[j].clear()
                self.str_y_law_training[j].clear()
            
            
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