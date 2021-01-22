# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 17:20:07 2021

@author: Kaichi Hamaishi
"""

class director:
    description="ディレクターの基底クラスです。"
    def __init__(self):
        pass
    def show_description(self):
        print(self.description)
    def make_map(self,floor,player,enemies,treasures):
        return[enemies[0],treasures[0]]