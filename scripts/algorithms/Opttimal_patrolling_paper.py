#!/usr/bin/env python3


import networkx as nx
from networkx.readwrite.graphml import GraphML
import numpy as np
from mrpp_sumo.srv import NextTaskBot, NextTaskBotResponse, AlgoReady, AlgoReadyResponse
from mrpp_sumo.msg import AtNode
import sys
import rospy
import rospkg

"""we need DFS tour not justs search"""
''' add call back next task'''

Graph_path = sys.argv[1]
no_off_agents = int(sys.argv[2])
graphML= nx.read_graphml(Graph_path)       #Reading the graphML file from the given input path

def DFSUtil(Graph, v, visited):
    '''The helper Recursive Function for DFS traversel'''
        # Mark the current node as visited and print it
    visited.append(v)
    #print(v)
 
        # recur for all the vertices adjacent to this vertex
    for neighbour in Graph.neighbors(v):
        if neighbour not in visited:
            visited = DFSUtil(Graph,neighbour, visited)
    if visited[-1] != v:
      visited.append(v)
    return visited


def DFS (Graph):
    '''This function takes a graph as input and return its Depth First Search
    # It uses recursive DFSUtil'''
    # create a list to store all visited vertices
    visited = list()
        # call the recursive helper function to print DFS traversal starting from all
        # vertices one by one
    for vertex in Graph.nodes:
        if vertex not in visited:
            visited = DFSUtil(Graph,vertex, visited)
    return visited

def partition(g,wg,l):
  a=0
  pi=[]
  while a<=wg[-1]:
    p = [(u) for (u) in g if wg[g.index(u)] <=(a+l) and wg[g.index(u)] >=a]
    pi.append(p)
    a = [(u) for (u) in g if wg[g.index(u)] >= (a+l)]
    c = []
    for u in a:
      c.append(wg[g.index(u)])
    if len(c)==0:
      return pi
    else:
      a=min(c)
  return pi



'''setting the parameters for partitioning'''
def optimal_partition(graphML,m):
  g=DFS(graphML) 
  wg=[0]
  for i in range(1,len(g)):
    dist = (i)*graphML.edges[g[i-1],g[i]]["length"]  #lenght of each edge is 100 which is added in chain graph. 
    wg.append(dist)
  #g=range(len(g))
  g=list(map(int,g))
  wg=list(map(int,wg))
  a = 0
  delta = 100
  epsilon = 0.01
  b = (wg[-1]+delta)/m
  l = (a+b)/2
  while (b-a)>2*epsilon:
    pi = partition(g,wg,l)
    if len(pi)>m:
      a=l
      l = (a + b)/2
  #    print(pi)
    else:
  #    print(pi)
      pis=pi
      b = l
      l = (a+b)/2
  return pis



class OPP:

  def __init__(self, g, num_bots):
    self.graph=g
    self.num_bots = num_bots
    self.stamp = 0
    rospy.Service('algo_ready', AlgoReady, self.callback_ready)
    self.ready = True


  def callback_ready(self, req):
    algo_name = req.algo
    if algo_name == 'Opttimal_patrolling_paper' and self.ready:
      return AlgoReadyResponse(True)
    else:
      return AlgoReadyResponse(False)

  def callback_next_task(self,req):
    node = req.node_done
    t = req.stamp
    bot = req.name
    pis=optimal_partition(self.graph,self.num_bots)
    node_list = pis[int(bot[-1])]
    if int(node)+5<=24:
      neigh = str(int(node)+5)
    else:
      neigh = str(int(node)-5)
    next_walk = [node, neigh]
    next_departs = [t]
    return NextTaskBotResponse(next_departs, next_walk)

if __name__ == '__main__':
  rospy.init_node('optimal', anonymous= True)
  dirname = rospkg.RosPack().get_path('mrpp_sumo')
  done = False
  graph_name = rospy.get_param('/graph')
  num_bots = int(rospy.get_param('/init_bots'))
  g = nx.read_graphml(dirname + '/graph_ml/' + graph_name + '.graphml')
  s=OPP(g,num_bots)
  #rospy.Subscriber('at_node', AtNode, s.callback_idle)
  rospy.Service('bot_next_task', NextTaskBot, s.callback_next_task)

  done = False
  while not done:
    done = rospy.get_param('/done')
