# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 00:57:35 2021

@author: Kaichi Hamaishi
"""

from player import player

class require_human(player):
    description="手動でのプレイ方法です。コマンドラインから操作します。"
    
    def battle_command(self,enemy):
        print("プレイヤーの生命力:"+str(self.hp)+"/"+str(self.max_hp))
        print("0: 攻撃 (攻撃力"+str(self.attack)+")")
        print("1: 防御 (防御力"+str(self.shield)+")")
        print("2: 爆弾を使う (2倍攻撃 残"+str(self.bomb)+")")
        print("3: 薬草を使う (生命全快 残"+str(self.herb)+")")
        
        command_avalable = False
        command = -1
        while(not command_avalable):
            print("コマンド?")
            command = int(input())
            command_avalable = (command==0) or (command==1) or (command==2 and self.bomb>0) or (command==3 and self.herb>0)
        self.battle_action(enemy,command)
    
    def map_command(self,ways):
        command_avalable = False
        command = -1
        while(not command_avalable):
            print("コマンド?")
            command = int(input())
            command_avalable = command>=0 and command<len(ways)
        return command
    
    
        
if __name__ == "__main__":
    require_human().show_description()