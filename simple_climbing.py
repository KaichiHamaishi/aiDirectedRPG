# -*- coding: utf-8 -*-
"""
Created on Mon May 24 15:28:27 2021

@author: Kaichi Hamaishi
"""

from director import director
import numpy as np
import copy
import random



class simple_climmbing(director):
    objects=None
    def __init__(self):
        #0:スライム,1:ゴブリン,2:ドラゴン,3:新しい鎧,4:新しい剣,5:新しい盾,6:爆弾,7:薬草,8:宿屋
        self.script=[[4,5],[0,0],[0,1],[1,8],[6,7],[3,0],[3,2],[0,1],[1,7],[6,8]]
        self.script_best=[]
        self.score_best=-100
    def make_map(self,floor,player,enemies,treasures):
        map_obj=np.asarray(enemies+treasures)
        if self.objects is None:
            self.objects=len(enemies)+len(treasures)
        return map_obj[self.script[floor]].tolist()
    def learn(self,reward):
        if(reward>self.score_best):
            self.script_best=copy.deepcopy(self.script)
        else:
            self.script=copy.deepcopy(self.script_best)
        self.script[random.randrange(10)]=[random.randrange(self.objects),random.randrange(self.objects)]
        
        
        
        