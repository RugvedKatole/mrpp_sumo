
import networkx as nx
import sys
import rospkg
import random as rn
import tpbp_functions as fn
import os
if __name__ == '__main__':
    dir_name = rospkg.RosPack().get_path('mrpp_sumo')
    if len(sys.argv[1:]) == 0:
        graph_name = ['grid_5_5', 'iitb','cair']
        #graph_name = ['st_line']
        multiplicity = 3
        num_priority=[4,5,6]
        #alg_ids = [6, 7, 8, 9]
        algo_name = ['tpbp_final','tpbp_alt1']
        vel = 10.
        coeff=" ".join(['1','10','0','0'])
        # prior_nodes = ['0', '4', '20', '24']
        # min_tp = fn.compute_min_tp(graph, prior_nodes)/vel
        # min_tp = 40.
        # lambda_priors = [0.0]
        # len_walks = [40, 80, 120]
        # max_divisions = 10
        # eps_prob = 0
        # max_bots = 6
        # threads = 10
        # episodes = 5000
        init_bots = list(range(1, 5))
        sim_length = 20000
        # discount_factors = [1]
        random_string  = 'tpbp'
        i = 0
        for _ in range(multiplicity):
            for ib in init_bots:            #number of bots 1,2,3,4
                for g in graph_name:        # selectin a graph from 3 graphs
                    for a in num_priority:
                        graph = nx.read_graphml(dir_name + '/graph_ml/' + g + '.graphml')
                        i += 1
                        prior_nodes = rn.sample(graph.nodes(), a)
                        loc=rn.sample(prior_nodes,ib)
                        min_tp=(fn.compute_min_tp(graph,prior_nodes))/vel
                        for algo in algo_name:
                           
                            with open(dir_name + '/config/' + algo + '/{}_{}.yaml'.format(algo, i), 'w') as f:
                                f.write('use_sim_time: true\n')
                                f.write('graph: {}\n'.format(g))
                                f.write('init_bots: {}\n'.format(ib))
                                f.write('priority_nodes: {}\n'.format(' '.join(list(map(str,prior_nodes)))))
                                f.write('time_periods: {}\n'.format(' '.join(list(map(str, [min_tp] * a)))))
                            # f.write('lambda_priority: {}\n'.format(l))
                            # f.write('length_walk: {}\n'.format(w))
                            # f.write('max_divisions: {}\n'.format(max_divisions))
                            # f.write('eps_prob: {}\n'.format(eps_prob))
                                f.write('init_locations: \'{}\'\n'.format(' '.join(loc)))
                                f.write('done: false\n')
                                f.write('sim_length: {}\n'.format(sim_length))
                            # f.write('discount_factor: {}\n'.format(d))
                            # f.write('num_episodes: {}\n'.format(episodes))
                            # f.write('num_threads: {}\n'.format(threads))
                            # f.write('max_bots: {}\n'.format(max_bots))
                            # f.write('random_string: {}{}\n'.format(random_string, i))
                                #f.write('random_string: tpbp_{}\n'.format(i))
                                f.write('random_string: {}_{}_{}\n'.format(algo,g,i))
                                f.write('algo_name: {}\n'.format(algo))
                                f.write('coefficients: {}\n'.format(coeff))
                                if algo == 'tpbp_alt1':
                                    f.write('depth: 5')
                        print (i)
    else:
        print ('Please pass the appropriate arguments')