# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 17:30:20 2021

@author: Kaichi Hamaishi
"""
from player import player

class treasure:
    def __init__(self,_name="unnamedTreasure",_heal=0,_max_hp=0,_attack=0,_shield=0,_bomb=0,_herb=0):
        self.name=_name
        self.heal=_heal
        self.max_hp=_max_hp
        self.attack=_attack
        self.shield=_shield
        self.bomb=_bomb
        self.herb=_herb
    def apply_treasure(self,_player):
        #if(not issubclass(type(_player),player)):
        #    raise Exception("Error: _player is not player")
        _player.max_hp+=self.max_hp
        _player.heal(self.heal)
        _player.attack+=self.attack
        _player.shield+=self.shield
        _player.bomb+=self.bomb
        _player.herb+=self.herb
        