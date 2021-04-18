# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 14:55:31 2021

@author: Kaichi Hamaishi
"""

from director import director

import numpy as np
import chainer
from chainer import cuda, Function, gradient_check, Variable 
from chainer import optimizers, serializers, utils
from chainer import Link, Chain, ChainList
import chainer.functions as F
import chainer.links as L


class DirectorChain(Chain):
    def __init__(self,input_count,output_count):
        super(DirectorChain, self).__init__(
            l1=L.Linear(input_count,6),
            l2=L.Linear(6,output_count)

        )
        
    def __call__(self,x,y):
        return F.mean_squared_error(self.fwd(x), y)

    def fwd(self,x):
         h1 = F.sigmoid(self.l1(x))
         h2 = self.l2(h1)
         return h2


class DQN_director_v1(director):
    description="ディレクションを記録しておき、その記録と報酬を学習データにする。"
    model=None
    
    def make_map(self,floor,player,enemies,treasures):
        result=[]
        map_obj=enemies+treasures
        player_status=np.array([player.status_array()])
        if self.model is None:
            self.model = DirectorChain(len(player_status),len(map_obj))
            self.optimizer = optimizers.SGD()
            self.optimizer.setup(self.model)
        xV=Variable(player_status)
        ans=self.model.fwd(xV).data
        result=map_obj[np.argsort(ans)[-1:-2:-1]]
        return result
    def learn(self,reward):
        pass