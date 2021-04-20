# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 17:08:48 2021

@author: Kaichi Hamaishi
"""

from player import player
from enemy import enemy

class rulebase(player):
    description="ルールベースで動作するプレイヤー。\n敵が技を出そうとしたら防御する。\n使ってちょうど倒せそうなら爆弾を使う。\nHPが5以下なら安全策をとる(戦闘の回避、薬草の使用)。"
    
    def battle_command(self,enemy):
        #print("プレイヤーの生命力:"+str(self.hp)+"/"+str(self.max_hp))
        #print("0: 攻撃 (攻撃力"+str(self.attack)+")")
        #print("1: 防御 (防御力"+str(self.shield)+")")
        #print("2: 爆弾を使う (2倍攻撃 残"+str(self.bomb)+")")
        #print("3: 薬草を使う (生命全快 残"+str(self.herb)+")")
        command=0
        if(enemy.notice==2):
            #技を予告されたら防御
            command=1
        if(self.bomb>0 and enemy.hp<self.attack*2 and enemy.hp>self.attack):
            #無駄にならないなら爆弾
            command=2
        if(self.hp<=5 and self.herb>0):
            #危ないなら回復
            command=3
        
        self.battle_action(enemy,command)
    
    def map_command(self,ways):
        if(len(ways)<=1):
            return 0
        if(self.hp<=5 and (type(ways[0]) is enemy)):
            return 1
        if(type(ways[0]) == type(ways[1]) and type(ways[0]) is enemy):
            if(ways[0].hp<ways[1].hp):
                return 0
            return 1
        
        return 0
    
    
        
if __name__ == "__main__":
    rulebase().show_description()