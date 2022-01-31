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
    algos=['tpbp_final','tpbp_util','tpbp_alt1','tpbp_util1']
    fig,axes = plt.subplot(3,4,figsize=(20,20))
    i=1
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
                sns.lineplot(ax=axes[k,j],data = df1.iloc[::1000], x = list(range(0,len(df1.loc[::1000])*1000,1000)), y = df1.loc[::1000, nodes].mean(axis = 1), legend = True, linewidth = 3)

                # if i == config['random_string']:
                    # if config['init_bots'] == 1:
                        # num = config['random_string'].split("_")
                        # df1 = pd.read_csv(sim_dir + '/{}_{}_node.csv'.format("_".join(name_list[:-1]),num[-1]))
                        # sns.lineplot(data = df1.iloc[::1000], x = list(range(0,21000,1000)), y = df1.loc[::1000, nodes].mean(axis = 1), legend = False, linewidth = 3)
            plt.title("{} robots and {} priority nodes".format(config['init_bots'],k+4))
            plt.xticks(rotation = 30)
            plt.ylabel('Node Idleness')
            plt.xlabel("time in seconds")
    plt.savefig('{}/avg_idle_sample_1.png'.format(dirname), bbox_inches='tight')



if __name__ == '__main__':
    main(['tpbp_final','grid_5_5'])
