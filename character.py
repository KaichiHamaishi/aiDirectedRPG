# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 16:39:48 2021

@author: Kaichi Hamaishi
"""

class character:
    name="character"
    max_hp=10
    hp=10
    attack=3
    shield=1
    guard=False
    def __init__(self):
        pass
    def heal(self,value):
        if(self.hp<=0):
            return
        value=int(value)
        self.hp=min(self.hp+value,self.max_hp)
        if(value!=0):
            print(self.name+": "+str(self.hp)+"/"+str(self.max_hp)+" ("+str(value)+")")
        if(self.hp<=0):
            print(self.name+"は倒れた")
    def give_damage(self,value):
        value=abs(value)
        if(self.guard):
            value=max(0,value-self.shield)
        self.heal(-value)
    
    