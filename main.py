# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 17:43:27 2021

@author: Kaichi Hamaishi
"""

from collections import deque
import numpy as np
import matplotlib.pyplot as plt

import game
from require_human import require_human
#from player import player as player_parent
from player_rulebase import rulebase
#from random_director import random_director
#from DQN_director_v7 import DQN_director_v7 as dqn
from DQN_random_v7 import DQN_random_v7 as dqn
from simple_climbing import simple_climmbing as climbing

def calc_score(chance,target):
    x=chance-target
    y=1-(x**2)*8
    return y

#player=require_human("プレイヤー")
player=rulebase("プレイヤー")
director=dqn()
#director=climbing()

print("クリア確率を計測するためのプレイ回数は？:")
time_play = int(input())
print("それを何回？:")
imput_time_span=input()
if imput_time_span=="highscore":
    time_span=-5
else:
    time_span = int(imput_time_span)
print("目標の平均到達階層は？(0.0~21.0):")
target_chance=float(input())

game_success=deque()
score_history=deque()
avg_history=deque()
if time_span>0:
    for span in range(time_span):
        #自動プレイ
        for play in range(time_play):
            player.reset()
            game_success.append(game.start_game(player,director,True))
        #自動プレイでのクリア確率を計測し、結果を表示
        print("\n"+str(span+1)+"回目の結果:")
        #chance=game_success/time_play
        #print("クリア確率:",chance)
        #learn_score=calc_score(chance,target_chance)
        print("到達:["+','.join(str(i) for i in sorted(list(game_success)))+"]")
        avg=np.average(np.array(game_success))
        std=np.std(np.array(game_success))
        print("平均:"+str(avg)+" 標準偏差:"+str(std))
        learn_score=abs(target_chance-avg)*-1.0
        print("報酬:",learn_score,"\n")
        #学習
        director.learn(learn_score)
        score_history.append(learn_score)
        avg_history.append(avg)
        game_success.clear()
        
else:
    highscore_count=0
    span=0
    while highscore_count<(-time_span):
        #自動プレイ
        for play in range(time_play):
            player.reset()
            game_success.append(game.start_game(player,director,True))
        #自動プレイでのクリア確率を計測し、結果を表示
        print("\n"+str(span+1)+"回目の結果:")
        #chance=game_success/time_play
        #print("クリア確率:",chance)
        #learn_score=calc_score(chance,target_chance)
        print("到達:["+','.join(str(i) for i in sorted(list(game_success)))+"]")
        avg=np.average(np.array(game_success))
        std=np.std(np.array(game_success))
        print("平均:"+str(avg)+" 標準偏差:"+str(std))
        learn_score=abs(target_chance-avg)*-1.0
        print("報酬:",learn_score,"\n")
        #学習
        director.learn(learn_score)
        score_history.append(learn_score)
        avg_history.append(avg)
        game_success.clear()
        if learn_score>-1:
            highscore_count+=1
        else:
            highscore_count=0
        
        span+=1
        if span%10==0:
            highscore_count=0
        
        

plt.plot(range(span+1),score_history,label="score")
plt.plot(range(span+1),avg_history,label="average")
plt.legend()
plt.show()
#学習結果を確かめるために手動プレイを開始
director.random=False
while True:
    game.start_game(require_human("人間のプレイヤー"), director,False)
    print("\n")
