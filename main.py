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
from DQN_director_v2 import DQN_director_v2
from DQN_director_v3 import DQN_director_v3

def calc_score(chance,target):
    x=chance-target
    y=1-(x**2)*8
    return y

#player=require_human("プレイヤー")
player=rulebase("プレイヤー")
director=DQN_director_v3()

print("クリア確率を計測するためのプレイ回数は？:")
time_play = int(input())
print("それを何回？:")
time_span = int(input())
print("目標のクリア確率は？(0.0~1.0):")
target_chance=float(input())

for span in range(time_span):
    game_success=0
    for play in range(time_play):
        player.reset()
        game_success+=game.start_game(player,director,True)
    print("\n"+str(span+1)+"回目の結果:")
    chance=game_success/time_play
    print("クリア確率:",chance)
    learn_score=calc_score(chance,target_chance)
    print("報酬:",learn_score,"\n")
    director.learn(learn_score)
        