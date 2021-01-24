# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 17:14:17 2021

@author: Kaichi Hamaishi
"""
import numpy as np
import sys
import copy

#敵クラス
from enemy import enemy
#宝箱クラス
from treasure import treasure

def start_game(_player,_director,silent=False):
    player=_player
    player.silent=silent
    director=_director
    enemies=[
        enemy("スライム",4,1,0,[0.5,0.5,0],silent),
        enemy("ゴブリン",8,3,1,[0.6,0.2,0.2],silent),
        enemy("ドラゴン",15,4,1,[0.6,0.1,0.3],silent)
        ]
    treasures=[
        #名前,HP回復,最大HP,攻撃力,防御力,ばくだん,やくそう の順
        treasure("新しい鎧",0,5,0,0,0,0),
        treasure("新しい剣",0,0,2,0,0,0),
        treasure("新しい盾",0,0,0,2,0,0),
        treasure("爆弾",0,0,0,0,1,0),
        treasure("薬草",0,0,0,0,0,1),
        treasure("宿屋",10,0,0,0,0,0)
        ]
    goal=10
    if(not silent):
        print("プレイヤー:"+str(type(player)))
        player.show_description()
        print("ディレクター:"+str(type(director)))
        director.show_description()
        print("階層:"+str(goal))
    start=""
    if(silent):
        start="y"
    while(not(start=="y" or start=="n")):
        print("\nゲームを開始しますか？[y/n]")
        start=input()
    if(start=="n"):
        sys.exit()
    
    floor=0
    while(floor<=goal):
        if(not silent):
            print("\n第"+str(floor)+"階")
            player.show_status()
        ways=[]
        if(floor==goal):
            ways=[enemy("ドラゴン",15,4,1,[0.6,0.1,0.3],silent)]#最後は必ず強敵を出す
        else:
            ways=director.make_map(floor,player,enemies,treasures)
        if(not silent):
            print("\n向かう先は...")
            for i in range(len(ways)):
                print(str(i)+": "+str(ways[i].name))
        choosen=player.map_command(ways)
        
        if(type(ways[choosen])==treasure):
            #宝箱
            if(not silent):
                print(ways[choosen].name+"を手に入れた")
            ways[choosen].apply_treasure(player)
        else:
            #戦闘
            enemy_battle=copy.deepcopy(ways[choosen])
            if(not silent):
                print(enemy_battle.name+"が現れた")
            while(enemy_battle.hp>0 and player.hp>0):
                notice=enemy_battle.notice_attack()
                if(notice==0):
                    if(not silent):
                        print(enemy_battle.name+"は攻撃しようとしている")
                elif(notice==1):
                    if(not silent):
                        print(enemy_battle.name+"は身を守っている")
                    enemy_battle.execute_attack(player)
                elif(notice==2):
                    if(not silent):
                        print(enemy_battle.name+"は技を繰り出そうとしている")
                if(not silent):
                    print()
                player.battle_command(enemy_battle)
                if(enemy_battle.hp>0 and notice!=1):
                    enemy_battle.execute_attack(player)
                if(enemy_battle.hp<=0):
                    if(not silent):
                        print("勝利！\n攻撃力+1！\n防御力+1！")
                    player.attack+=1
                    player.shield+=1
                if(player.hp<=0):
                    if(not silent):
                        print("敗北した...")
            
        if(player.hp<=0):
            floor=goal
        
        floor+=1
        
    game_success=player.hp>0
    if(game_success):
        if(not silent):
            print("クリア！")
        return 1
    else:
        if(not silent):
            print("ゲームオーバー")
        return 0


if __name__ == "__main__":
    from require_human import require_human
    from random_director import random_director
    start_game(require_human("プレイヤー",10,3,1,1,1), random_director())

