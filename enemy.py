# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 16:41:21 2021

@author: Kaichi Hamaishi
"""

from character import character
import random

class enemy(character):
    chances=[1.0,0.0,0.0] #攻撃,防御,必殺 の順
    notice=-1
    def __init__(self,_name,_hp,_attack,_shield,_chances):
        if(type(_chances) is not list):
            raise Exception("Error on enemy.__init__: '_chance' is not list")
        
        self.name=_name
        self.max_hp=_hp
        self.hp=_hp
        self.attack=_attack
        self.shield=_shield
        self.chances=_chances
    def notice_attack(self):
        rand=random.uniform(0,sum(self.chances))
        for ind,val in enumerate(self.chances):
            if(val>rand):
                self.notice=ind
                break
            rand-=val
        return self.notice
    def execute_attack(self,_character):
        if(self.notice<0):
            self.notice_attack()
        
        self.guard=False
        
        if self.notice==0:
            print(self.name+"は攻撃した")
            _character.give_damage(self.attack)
        elif self.notice==2:
            print(self.name+"は技を繰り出した")
            _character.give_damage(self.attack*2)
        else:
            self.guard=True
        self.notice=-1
