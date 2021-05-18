# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 17:43:27 2021

@author: Kaichi Hamaishi
"""

import game
from require_human import require_human
#from player import player as player_parent
from player_rulebase import rulebase
#from random_director import random_director
from DQN_random_director import DQN_random_director as dqn

def calc_score(chance,target):
    x=chance-target
    y=1-(x**2)*8
    return y

#player=require_human("プレイヤー")
player=rulebase("プレイヤー")
director=dqn()

print("クリア確率を計測するためのプレイ回数は？:")
time_play = int(input())
print("それを何回？:")
time_span = int(input())
print("目標のクリア確率は？(0.0~1.0):")
target_chance=float(input())

for span in range(time_span):
    game_success=0
    #自動プレイ
    for play in range(time_play):
        player.reset()
        game_success+=game.start_game(player,director,True)
    #自動プレイでのクリア確率を計測し、結果を表示
    print("\n"+str(span+1)+"回目の結果:")
    chance=game_success/time_play
    print("クリア確率:",chance)
    learn_score=calc_score(chance,target_chance)
    print("報酬:",learn_score,"\n")
    #学習
    director.learn(learn_score)

#学習結果を確かめるために手動プレイを開始
game.start_game(require_human("人間のプレイヤー"), director,False)
