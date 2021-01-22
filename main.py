# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 17:43:27 2021

@author: Kaichi Hamaishi
"""

import game
from require_human import require_human
from random_director import random_director
game.start_game(require_human("プレイヤー",10,3,1,1,1), random_director())