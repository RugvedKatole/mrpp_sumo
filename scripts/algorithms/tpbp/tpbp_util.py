#!/usr/bin/env python3

'''
TPBP util

ROS Parameters -
1. graph
2. priority_nodes
3. time_periods
4. coefficients
5. num_dummy_nodes
6. reshuffle_time
7. random_string  (folder name)
'''
import rospy
import rospkg
import networkx as nx
import os
import numpy 

from mrpp_sumo.srv import NextTaskBot, NextTaskBotResponse
from mrpp_sumo.srv import AlgoReady, AlgoReadyResponse
from mrpp_sumo.msg import AtNode
import time
import random as rn
import numpy as np


def add_vertex_trail(graph, path, len_path, vertex, dest, len_max):
    cur = path[-1]
    len_rem = nx.dijkstra_path_length(graph, cur, dest, weight = 'length')
    if (len_rem + len_path) > len_max:
        return False
    if not cur in path[:-1]:
        return True
    for i in range(len(path[:-2])):
        if path[i] == cur and path[i + 1] == vertex:
            return False
    return True

def compute_valid_trails(graph, source, dest, len_max, folder):
    if os.path.exists(folder + '/valid_trails_{}_{}_{}.in'.format(str(source), str(dest),str(int(len_max)))):
        return
    with open(folder + '/valid_trails_{}_{}_{}.in'.format(str(source), str(dest),str(int(len_max))), 'w') as f:
        with open(folder + '/vp_temp_{}.in'.format(0), 'w') as f1:
            f1.write(str(source) + ' ' + str(0) + '\n')
        count = 1  #no of walks in vp temp
        steps = 0   # iterations on vp temp
        while count != 0:
            count = 0
            with open(folder + '/vp_temp_{}.in'.format(steps), 'r') as f0:
                with open(folder + '/vp_temp_{}.in'.format(steps + 1), 'w') as f1:
                    for line in f0:
                        line1 = line.split('\n')
                        line_temp = line1[0]
                        line1 = line_temp.split(' ')
                        path = list(map(str, line1[:-1]))
                        len_path = float(line1[-1])
                        neigh = graph.neighbors(path[-1])

                        for v in neigh:
                            ## VELOCITY is set to 10.m/s
                            if add_vertex_trail(graph, path, len_path, v, dest, len_max * 10.):
                                temp = ' '.join(line1[:-1])
                                temp = temp + ' ' + str(v)
                                if v == dest:
                                    f.write(temp + '\n')
                                else:
                                    count += 1
                                    temp += ' ' + str(graph[path[-1]][v]['length'] + len_path)
                                    f1.write(temp + '\n')
            steps += 1
            os.remove(folder + '/vp_temp_{}.in'.format(steps-1))
    os.remove(folder + '/vp_temp_{}.in'.format(steps))
    #for i in range(steps + 1):
    #    os.remove(folder + '/vp_temp_{}.in'.format(i))


def all_valid_trails(graph, node_set, len_max, folder):
    #suggestion using j in range(i+1,len(node_set)) might help reducing time complexity to n(n-1)/2, current time complexity is n^2
    for i in range(len(node_set)):
        for j in range(len(node_set)):
            compute_valid_trails(graph, node_set[i], node_set[j], len_max[i], folder)


class TPBP:

    def __init__(self, graph, priority_nodes, time_periods, coefficients,path_to_folder):
        '''Initializes class TPBP with required ros paramenters  i.e time periods,dummy nodes reshuffle time,etc '''
        #velocity
        self.v_max=10
        self.robots = {}
        self.ready = False
        rospy.Service('algo_ready', AlgoReady, self.callback_ready)
        self.graph = graph          #assigning graph to self 
        self.priority_nodes = priority_nodes     
        self.time_periods = time_periods
        self.coefficients = coefficients
        self.graph_name = graph_name
        self.offline_folder = path_to_folder   #offline folder path to store valid walks
        for node in self.graph.nodes():
            self.graph.nodes[node]['idleness'] = 0.     #adding a idleness parameter to nodes
            self.graph.nodes[node]['future_visits'] = {}
        self.stamp = 0.         #initializing time stamp to 0
        # for edge in self.graph.edges():
        #     self.graph[edge[0]][edge[1]]['duration'] = self.graph[edge[0]][edge[1]]['length']/self.v_max
        #self.num_dummy_nodes = num_dummy_nodes #Number of dummy nodes
        #self.reshuffle_time = reshuffle_time #Expected Time between reshuffles
        #self.dummy_time_period = [self.time_periods[0]] * self.num_dummy_nodes
        #self.time_periods.extend(self.dummy_time_period)        
        self.nodes = list(self.graph.nodes())
        #self.non_priority_nodes = [item for item in self.nodes if item not in self.priority_nodes]  # all nodes which are not in priority nodes
        #self.dummy_nodes = np.random.choice(self.non_priority_nodes, self.num_dummy_nodes) #selecting dummy nodes at random from non-priority nodes
        #self.priority_nodes_cur = self.priority_nodes[:]            #list of current priority nodes
        #self.priority_nodes_cur.extend(self.dummy_nodes)            # adding dummy nodes to priority nodes list
        #self.priority_nodes_prev = self.priority_nodes_cur[:]
        #self.reshuffle_next = np.random.poisson(self.reshuffle_time)
        #self.non_priority_nodes = [item for item in self.nodes if item not in self.priority_nodes]  #choosing dummy nodes other than current
        self.N = len(self.nodes)
        self.assigned = []
        #self.non_priority_assigned = []
        for _ in self.priority_nodes:
            self.assigned.append(False)

        self.tpbp_offline()

    def tpbp_offline(self):
        if not os.path.isdir(self.offline_folder):
            '''creates a offline folder is not created already'''
            os.mkdir(self.offline_folder)
        #n = len(list(self.graph.nodes()))
        s = len(self.priority_nodes)
        temp = self.time_periods.copy()
        for _ in range(s):
            ''' assigning time periods to non priority nodes'''
            temp.append(self.time_periods[0])
        all_valid_trails(self.graph, self.priority_nodes, temp, self.offline_folder)
        time.sleep(1.)  #halts the exceution of code for 1 sec
        self.ready = True
    ''' add FHUM reward ,lamba = 10'''
    
    # def tpbp_reward(self, walk):
    #     nodes = list(set(walk))
    #     temp1 = 0.
    #     temp2 = 0.
    #     for i in nodes:
    #         temp1 += self.graph.nodes[i]['idleness']
    #         if i in self.priority_nodes:
    #             j = self.priority_nodes.index(i)    #returns index of i in list priority_nodes, i,j is node index pair
    #             if not self.assigned[j]:
    #                 temp2 += max(self.graph.nodes[i]['idleness'] - self.time_periods[j], 0)

    #     temp3 = 0.
    #     '''
    #     for i in range(len(self.priority_nodes)):
    #         if not self.assigned[i] and not self.priority_nodes[i] in nodes:
    #             dist = np.inf
    #             for j in nodes:
    #                 temp = nx.dijkstra_path_length(self.graph, j, self.priority_nodes[i], 'length')
    #                 if temp < dist:
    #                     dist = temp
    #             temp3 += dist'''
    #     temp4 = 0
    #     '''
    #     for i in range(len(walk) - 1):
    #         temp4 += self.graph[walk[i]][walk[i + 1]]['length']'''
        
    #     return np.dot([temp1, temp2, temp3, temp4], coefficients)

    def utility(self,walk):
        reward = 0
        # n= [self.graph[i][j]['duration'] for i,j in dict(zip(walk[:-1],walk[1:])).items()]
        n=[0]
        node_val = np.zeros(self.N)
        future_visit_final = {}
        for i, w in enumerate(self.nodes):
            node_val[i] = self.graph.nodes[w]['idleness']
            if len(self.graph.nodes[w]['future_visits'].values()) > 0:
                future_visit_final[w] = max(self.graph.nodes[w]['future_visits'].values())
            else:
                future_visit_final[w] = -1. * node_val[i]

        # Utility maximization code

        for i,j,z in list(zip(walk[:-1],walk[1:],list(range(len(walk)-1)))):
            n.append(n[z]+self.graph[i][j]['length']/self.v_max)
        for t,i in enumerate(walk):
            # flag=False
            if future_visit_final[i] > n[t]:
                # print("1st conditoon")
                reward += 0
            # for j in future_visit_final:
            #     if n[t] < j:
            #         reward += 0
            #         flag=True
            #         break
            # if not flag:
            else:
                #reward += self.graph.nodes[i]['idleness'] + n[t]
                reward += n[t] - future_visit_final[i]
                if i in self.priority_nodes:
                    # for j in self.graph.nodes[i]['future_visits'].values():
                    if n[t] - future_visit_final[i] < self.time_periods[0]:    #bit hard code here, j+ idleness is expected idlesness
                        reward += (self.coefficients[1])*(n[t] - future_visit_final[i])
                    else:
                        reward += self.coefficients[1]*self.time_periods[0]
                    future_visit_final[i]=n[t]
        return reward  


    def callback_idle(self, data):
        #Update Idleness
        if self.stamp < data.stamp:
            dev = data.stamp - self.stamp
            self.stamp = data.stamp
            for i in self.graph.nodes():
                self.graph.nodes[i]['idleness'] += dev
                for j in self.graph.nodes[i]['future_visits'].keys():
                    self.graph.nodes[i]['future_visits'][j] -= dev

            for i, n in enumerate(data.node_id):
                self.graph.nodes[n]['idleness'] = 0.
                if data.robot_id[i] in self.graph.nodes[n]['future_visits'].keys():
                    if self.graph.nodes[n]['future_visits'][data.robot_id[i]] < 0.:
                        self.graph.nodes[n]['future_visits'].pop(data.robot_id[i])


        #Randomization Code
        '''
        if self.stamp >= self.reshuffle_next:
            self.reshuffle_next = self.stamp + numpy.random.poisson(self.reshuffle_time)
            self.dummy_nodes = numpy.random.choice(self.non_priority_nodes, self.num_dummy_nodes)
            self.priority_nodes_prev = self.priority_nodes_cur[:]
            self.priority_nodes_cur = self.priority_nodes[:]
            self.priority_nodes_cur.extend(self.dummy_nodes)
            self.assigned_prev = self.assigned[:]
            self.non_priority_nodes = [item for item in self.nodes if item not in self.priority_nodes_cur]

            for i, n in enumerate(self.dummy_nodes):
                self.assigned[len(self.priority_nodes) + i] = False
                if n in self.priority_nodes_prev:
                    n_prev = self.priority_nodes_prev.index(n)
                    self.assigned[len(self.priority_nodes) + i] = self.assigned_prev[n_prev]'''

    def callback_next_task(self, req):
        t = req.stamp
        node = req.node_done


        #if node in self.non_priority_assigned:
        #    self.non_priority_assigned.remove(node)

        if node in self.priority_nodes:
            self.assigned[self.priority_nodes.index(node)] = False

        print (node, self.priority_nodes, self.assigned)

        best_reward = -np.inf
        next_walk = []

        self.graph.nodes[node]['idleness'] = 0.

        for j in range(len(self.priority_nodes)):
            if not self.assigned[j]:
                valid_trails = '/valid_trails_{}_{}_{}.in'.format(node, self.priority_nodes[j], str(int(self.time_periods[j])))
                with open(self.offline_folder + valid_trails, 'r') as f:
                    count = 0
                    for line in f:
                        count += 1
                        line1 = line.split('\n')
                        line2 = line1[0].split(' ')
                        r = self.utility(line2)
                        if r > best_reward:
                            best_reward = r
                            next_walk = line2
        '''
        if all(self.assigned):
            print ('alive')
            idles = []
            for i in self.non_priority_nodes:
                idles.append(self.graph.nodes[i]['idleness'])

            max_id = 0
            max_ids = list(np.where(idles == np.amax(idles))[0])
            max_id = rn.sample(max_ids, 1)[0]
            dest_node = self.non_priority_nodes[max_id]
            temp = self.non_priority_nodes.copy()
            while dest_node in self.non_priority_assigned or dest_node == node:
                if len(temp) == 1:
                    if dest_node == node:
                        temp1 = self.non_priority_nodes.copy()
                        temp1.remove(node)
                        dest_node = rn.sample(temp1, 1)[0]
                    break
                else:
                    temp.remove(dest_node)
                    idles.pop(max_id)
                    max_ids = list(np.where(idles == np.amax(idles))[0])
                    max_id = rn.sample(max_ids, 1)[0]
                    dest_node = temp[max_id]
            if not dest_node in self.non_priority_assigned:
                self.non_priority_assigned.append(dest_node)
            next_walk = nx.dijkstra_path(g, node, dest_node, 'length')
        
        else:
            self.assigned[self.priority_nodes.index(next_walk[-1])] = True'''

        next_departs = [t] * (len(next_walk) - 1)
        
        return NextTaskBotResponse(next_departs, next_walk)


    def callback_ready(self, req):
        algo_name = req.algo
        if algo_name == 'tpbp_util' and self.ready:
            return AlgoReadyResponse(True)
        else:
            return AlgoReadyResponse(False)

if __name__ == '__main__':
    rospy.init_node('tpbp_util', anonymous = True)
    dirname = rospkg.RosPack().get_path('mrpp_sumo')
    done = False
    graph_name = rospy.get_param('/graph')
    g = nx.read_graphml(dirname + '/graph_ml/' + graph_name + '.graphml')
    algo_name=rospy.get_param('/algo_name')
    priority_nodes = rospy.get_param('/priority_nodes').split(' ')
    time_periods = list(map(float, rospy.get_param('/time_periods').split(' ')))
    coefficients = list(map(float, rospy.get_param('/coefficients').split(' ')))
    #folder = rospy.get_param('/random_string')
    folder = algo_name + graph_name
    #num_dummy_nodes = rospy.get_param('/num_dummy_nodes')
    #reshuffle_time = rospy.get_param('/reshuffle_time')
    path_to_folder = dirname + '/outputs/' + folder
    s = TPBP(g, priority_nodes, time_periods, coefficients, path_to_folder)

    rospy.Subscriber('at_node', AtNode, s.callback_idle)
    rospy.Service('bot_next_task', NextTaskBot, s.callback_next_task)
    done = False
    while not done:
        done = rospy.get_param('/done')
        rospy.sleep(0.1)
