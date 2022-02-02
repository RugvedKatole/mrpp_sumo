from turtle import color
import seaborn as sns
import networkx as nx
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import rospkg
import pandas as pd
import numpy as np
import yaml
import math
import matplotlib.cm as cm
import matplotlib
import os, sys, shutil
import plotly
import kaleido
import plotly.io as pio



def main(param):
    dirname = rospkg.RosPack().get_path('mrpp_sumo')
    name = param[0]
    g = param[1]
    # edges = [graph[e[0]][e[1]]['name'] for e in list(graph.edges())]

    # tpbp_df=pd.read_csv(dirname+'/{}.csv'.format(name))
    plt.figure()
    sns.set_style('white')
    sns.set_context(font_scale= 1, rc = {"font.size" : 15, "axes.titlesize" : 20})
    plt.suptitle('Node Idleness Values vs Time', size = 18, y = 1.02, x = 0.4)
    # for i in tpbp_df['random_string']:
    # for i in range(1,12,3):
    algos=['tpbp_final','tpbp_alt1','tpbp_util','tpbp_util1']
    fig,axes = plt.subplots(3,4,figsize=(30,15))
    i=0
    for j in range(4):
        for k in range(3):
            i += 1
            for a in algos:
                
                with open('{}/config/{}/{}.yaml'.format(dirname,a,a + "_" + str(i)), 'r') as f:
                    config = yaml.load(f, yaml.FullLoader)
                graph = nx.read_graphml(dirname + '/graph_ml/{}.graphml'.format(config['graph']))
                sim_dir = dirname + '/post_process/' + a + "_" + str(i)
                nodes = list(graph.nodes())
                df1 = pd.read_csv(sim_dir + '/{}_{}_node.csv'.format(a,str(i)))
                priority_nodes = config['priority_nodes'].split(' ')
                non_priority_nodes = [u for u in graph.nodes if u not in priority_nodes]
                time_period = config['time_periods'].split(' ')
                sns.lineplot(ax=axes[k,j],data = df1.iloc[::1000], x = list(range(0,len(df1.loc[::1000])*1000,1000)), y = df1.loc[::1000, nodes].mean(axis = 1), legend = True, linewidth = 3,alpha=0.4)
                # sns.lineplot(ax=axes[k,j],data = df1.iloc[::1000], x = list(range(0,len(df1.loc[::1000])*1000,1000)), y = df1.loc[::1000, priority_nodes].mean(axis = 1), legend = True, linewidth = 3)
            axes[k,j].set_title("{} robots and {} priority nodes".format(config['init_bots'],k+4))
            axes[k,j].set_ylim(0,500)
            # axes[k,j].set_xlim(0)
            sns.lineplot(ax=axes[k,j],data = df1.iloc[::1000], x = list(range(0,len(df1.loc[::1000])*1000,1000)), y = float(time_period[0]), legend = True, linewidth = 3,alpha=0.4)
            axes[k,j].legend(algos,prop={'size': 9})
            # axes[k,j].set_xlabel('time in seconds')
            plt.xticks(rotation = 30)
            plt.ylabel('Node Idleness')
            plt.xlabel("time in seconds")
    plt.savefig('{}/avg_idle_ample_1.png'.format(dirname), bbox_inches='tight')



if __name__ == '__main__':
    main(['tpbp_final','grid_5_5'])
