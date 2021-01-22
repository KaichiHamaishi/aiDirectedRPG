# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 13:51:28 2021

@author: Kaichi Hamaishi
"""

from director import director
import random

class random_director(director):
    description="プレイヤーの資源と関係なくランダムにゲームを進行します。"
    def make_map(self,floor,player,enemies,treasures):
        result=[]
        for i in range(2):
            if(random.random()<0.5):
                result.append(enemies[int(random.uniform(0,len(enemies)))])
            else:
                result.append(treasures[int(random.uniform(0,len(treasures)))])
        return result