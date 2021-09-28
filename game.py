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

def get_floors():
    return 10

def start_game(_player,_director,silent=False):
    player=_player
    player.silent=silent
    director=_director
    goal=get_floors()
    enemies=[
        #名前、HP、攻撃力、防御力、行動の確率[攻撃,防御,必殺]、経験値　の順
        enemy("スライム Lv1",4,1,1,[0.5,0.5,0],1,silent),
        enemy("スライム Lv2",5,1,1,[0.5,0.5,0],1,silent),
        enemy("スライム Lv3",5,1,2,[0.5,0.5,0],2,silent),
        enemy("スライム Lv4",6,1,2,[0.5,0.5,0],2,silent),
        enemy("スライム Lv5",7,2,2,[0.5,0.5,0],3,silent),
        enemy("スライム Lv6",8,2,2,[0.5,0.5,0],3,silent),
        enemy("スライム Lv7",9,3,3,[0.5,0.5,0],4,silent),
        enemy("スライム Lv8",10,3,3,[0.5,0.5,0],4,silent),
        enemy("スライム Lv9",11,3,4,[0.5,0.5,0],5,silent),
        enemy("スライム Lv10",12,3,4,[0.5,0.5,0],5,silent),
        
        enemy("ゴブリン Lv1",3,2,1,[0.6,0.2,0.2],1,silent),
        enemy("ゴブリン Lv2",4,3,1,[0.6,0.2,0.2],1,silent),
        enemy("ゴブリン Lv3",5,4,1,[0.6,0.2,0.2],2,silent),
        enemy("ゴブリン Lv4",6,5,1,[0.6,0.2,0.2],2,silent),
        enemy("ゴブリン Lv5",7,6,2,[0.6,0.2,0.2],3,silent),
        enemy("ゴブリン Lv6",8,7,2,[0.6,0.2,0.2],3,silent),
        enemy("ゴブリン Lv7",9,8,2,[0.6,0.2,0.2],4,silent),
        enemy("ゴブリン Lv8",10,9,2,[0.6,0.2,0.2],4,silent),
        enemy("ゴブリン Lv9",11,10,3,[0.6,0.2,0.2],5,silent),
        enemy("ゴブリン Lv10",12,11,3,[0.6,0.2,0.2],5,silent),
        
        enemy("ドラゴン",50,8,3,[0.6,0.1,0.3],10,silent)
        ]
    #enemies=list(map(
    #    lambda t:enemy(
    #        "スライム Lv"+str(t),
    #        int(t*1),int(t*0.75),int(t*1.25),
    #        [0.5,0.5,0],silent
    #        ),range(1,10)
    #    ))
    #enemies.extend(map(
    #    lambda t:enemy(
    #        "ゴブリン Lv"+str(t),
    #        int(t*1),int(t*1.25),int(t*0.75),
    #        [0.5,0.5,0],silent),
    #    range(1,10)))
    #enemies.extend(map(
    #    lambda t:enemy(
    #        "ウルフ Lv"+str(t),
    #        int(t*1.25),int(t*1),int(t*0.75),
    #        [0.5,0.5,0],silent),
    #    range(1,10)))
    #enemies.append(enemy("ドラゴン",goal*2.5,goal*0.25,goal*0.15,[0.6,0.1,0.3],silent))
            
    treasures=[
        #名前,HP回復,最大HP,攻撃力,防御力,ばくだん,やくそう の順
        treasure("新しい鎧",0,5,0,0,0,0),
        treasure("新しい剣",0,0,2,0,0,0),
        treasure("新しい盾",0,0,0,2,0,0),
        treasure("爆弾",0,0,0,0,1,0),
        treasure("薬草",0,0,0,0,0,1),
        treasure("宿屋",10,0,0,0,0,0)
        ]
    
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
            print("\n目的地まであと"+str(goal-floor)+"km")
            print(">"+("-"*goal)+"<")
            print(" "+(" "*floor)+"^")
            player.show_status()
        ways=[]
        if(floor==goal):
            ways=[enemy("ドラゴン",goal*2.5,goal*0.25,goal*0.15,[0.6,0.1,0.3],0,silent)]#最後は必ず強敵を出す
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
                        print("勝利！")
                        if(enemy_battle.exp>0):
                            print("最大HP,攻撃力,防御力が"+str(enemy_battle.exp)+"上昇！")
                    player.max_hp+=enemy_battle.exp
                    player.attack+=enemy_battle.exp
                    player.shield+=enemy_battle.exp
                if(player.hp<=0):
                    if(not silent):
                        print("敗北した...")
            
        if(player.hp<=0):
            return floor
        
        floor+=1
    return floor
    #game_success=player.hp>0
    #if(game_success):
    #    #print("クリア！")
    #    return 1
    #else:
    #    #print("ゲームオーバー")
    #    return 0


if __name__ == "__main__":
    from require_human import require_human
    from random_director import random_director
    start_game(require_human("プレイヤー",10,3,1,1,1), random_director())

