# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 00:41:00 2021

@author: Kaichi Hamaishi
"""
from character import character

class player(character):
    description="プレイヤーの基底クラスです。ぜんぶ0番目の選択肢を選びます。"
    bomb=1
    herb=1
    def __init__(self,_name="unnamed",_hp=10,_attack=3,_shield=1,_bomb=1,_herb=1):
        self.name=_name
        self.max_hp=_hp
        self.hp=_hp
        self.attack=_attack
        self.shield=_shield
        self.bomb=_bomb
        self.herb=_herb
    def reset(self,_hp=10,_attack=3,_shield=1,_bomb=1,_herb=1):
        self.max_hp=_hp
        self.hp=_hp
        self.attack=_attack
        self.shield=_shield
        self.bomb=_bomb
        self.herb=_herb
    def show_description(self):
        print(self.description)
    def show_status(self):
        if(not self.silent):
            print(
                  "生命力: "+str(self.hp)+"/"+str(self.max_hp)+"\n"+
                  "攻撃力: "+str(self.attack)+"\n"+
                  "防御力: "+str(self.shield)+"\n"+
                  "爆弾:   "+str(self.bomb)+"\n"+
                  "薬草:   "+str(self.herb)
                  )
    
    def battle_command(self,enemy):
        self.battle_action(enemy,0)
    def map_command(self,ways):
        return 0
    def battle_action(self,enemy,command):
        self.guard=False
        
        if(command==0):
            if(not self.silent):
                print(self.name+"は攻撃した")
            enemy.give_damage(self.attack)
        elif(command==1):
            if(not self.silent):
                print(self.name+"は身を守った")
            self.guard=True
        elif(command==2):
            if(not self.silent):
                print(self.name+"は爆弾を敵に投げつけた")
            enemy.give_damage(self.attack*2)
            self.bomb-=1
        elif(command==3):
            if(not self.silent):
                print(self.name+"は薬草を傷口に塗った")
            self.hp=self.max_hp
            self.herb-=1
            
    def status_array(self):
        return[
            self.max_hp,
            self.hp,
            self.attack,
            self.shield,
            self.bomb,
            self.herb
            ]
    
if __name__ == "__main__":
    player().show_description()