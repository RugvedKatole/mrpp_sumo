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
    name_list =name.split('_')
    sim_dir = dirname + '/post_process/' + name
    with open('{}/config/{}/{}.yaml'.format(dirname,"_".join(name_list[:-1]),name), 'r') as f:
        config = yaml.load(f, yaml.FullLoader)
    graph = nx.read_graphml(dirname + '/graph_ml/{}.graphml'.format(config['graph']))
    nodes = list(graph.nodes())
    # edges = [graph[e[0]][e[1]]['name'] for e in list(graph.edges())]
    priority_nodes = config['priority_nodes'].split(' ')
    time_period = config['time_periods'].split(' ')
    n = len(nodes)
    # num_bots = int(config['init_bots'])
    # sim_length = int(config['sim_length'])
    # algo_name = config['algo_name']
    non_priority_nodes = [u for u in graph.nodes if u not in priority_nodes]
    node_x = []
    node_y = []
    node_x_priority= []
    node_y_priority= []
    avg_idle = []
    max_idle = []
    nodes = list(graph.nodes)
    non_priority_nodes = [u for u in graph.nodes if u not in priority_nodes]
    # print(non_priority_nodes,priority_nodes)
    for node in graph.nodes():
        x, y = graph.nodes[node]['x'], graph.nodes[node]['y']
        if node in priority_nodes:
            node_x_priority.append(x)
            node_y_priority.append(y)
        else:
            node_x.append(x)
            node_y.append(y)

    d = 20 #radius of nodes
    edge_vis = {'cair': d/2, 'circle': d/2, 'grid_5_5': d/2, 'iitb': d, 'ladder': d/2, 'st_line': d, 'st_line_assym': d}
    s = int(edge_vis[config['graph']])
    # print(s)
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = graph.nodes[edge[0]]['x'], graph.nodes[edge[0]]['y']
        x1, y1 = graph.nodes[edge[1]]['x'], graph.nodes[edge[1]]['y']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    df1 = pd.read_csv(sim_dir + '/{}_node.csv'.format(name))
    idleness_over=[]
    df4=df1
    for n in df1.columns:
        print(n)
        # idleness_over.append(df1[n].value_counts()[1])
        for i in df1[n]:
            df4[n][i]=(max(i-80,0))
    # print(i)

    df4.to_csv(sim_dir + '/{}_overshoot.csv'.format(name),index=False)

    for n in df4.columns:
        idleness_over.append(df4[n].value_counts()[1])

    #plotting priority node locations
    def plot_priority_nodes(node_x,node_y,node_x_priority,node_y_priority):
        non_priority = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale='Blues',
                reversescale=False,
                color=1,
                size=2 * d,
                # opacity = 0.5,
                # showscale = False,
                # colorbar=dict(
                #     thickness=15,
                #     title='Node Connections',
                #     xanchor='left',
                #     titleside='right'
                # ),
                line_width=0))
        priority = go.Scatter(
        x=node_x_priority, y=node_y_priority,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Reds',
            reversescale=False,
            color=1,
            size=2 * d,
            # opacity = 0.5,
            # showscale = False,
            # colorbar=dict(
            #     thickness=15,
            #     title='Node Connections',
            #     xanchor='left',
            #     titleside='right'
            # ),
            line_width=0))

        fig = go.Figure(data=[non_priority,priority],
                    layout=go.Layout(
                    # title='Graph \'{}\''.format(config['graph']),
                    # titlefont_size=16,
                    showlegend=True,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=0,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), 
                    width=1200,
                    height=1000)
                    )

        # fig.add_trace(go.Heatmap(x = node_x, y = node_y, z = node_z))
        for i in range(0, len(edge_x), 3):
            # print (edge_x[i])
            x1 = edge_x[i + 1]  # arrows' head
            y1 = edge_y[i + 1]  # arrows' head
            x0 = edge_x[i]  # arrows' tail
            y0 = edge_y[i]  # arrows' tail
            # print (x0, y0, x1, y1)

            vert = True
            if x0 != x1:
                m = (y1 - y0)/(x1 - x0)
                c = y0 - m * x0
                vert = False
            
            if vert:
                yt = y0 + s * np.sign(y1 - y0)
                yh = y1 - s * np.sign(y1 - y0)
                xt = x0
                xh = x1
            else:
                if y1 == y0:
                    xt = x0 + s * np.sign(x1 - x0)
                    xh = x1 - s * np.sign(x1 - x0)
                    yt = y0
                    yh = y1
                else:
                    xt = x0 + math.sqrt(s ** 2 / (m ** 2 + 1)) * np.sign(x1 - x0)
                    xh = x1 - math.sqrt(s ** 2 / (m ** 2 + 1)) * np.sign(x1 - x0)
                    yt = m * xt + c
                    yh = m * xh + c
            

            fig.add_annotation(
                x=xh,  # arrows' head
                y=yh,  # arrows' head
                ax=xt,  # arrows' tail
                ay=yt,  # arrows' tail
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                text='',  # if you want only the arrow
                showarrow=True,
                arrowhead=1,
                arrowsize=2,
                arrowwidth=1,
                arrowcolor='black'
                )
        fig.update_yaxes(
            scaleanchor = "x",
            scaleratio = 1,
        )
        fig.update_layout(title_text='Priority Node Loctions', title_x=0.5, titlefont_size = 20, plot_bgcolor = 'rgba(0, 0, 0, 0)')
        fig.to_image(format="png", engine="kaleido")
        fig.write_image('{}/{}_Priority_nodes.png'.format(sim_dir, name))
        del fig
        # fig.show()

    #ploting spatial graph of idleness overshoot
    def idleness_spatial():
            node_trace2 = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale='Blackbody',
                reversescale=False,
                color=[],
                size=2 * d,
                opacity = 0.2,
                # showscale = False,
                # colorbar=dict(
                #     thickness=15,
                #     title='Node Connections',
                #     xanchor='left',
                #     titleside='right'
                # ),
                line_width=0))

            node_trace3 = go.Scatter(
            x=node_x_priority, y=node_y_priority,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale='Bluered',
                reversescale=False,
                color=idleness_over,
                size=2 * d,
                opacity = 1,
                # showscale = False,
                # colorbar=dict(
                #     thickness=15,
                #     title='Node Connections',
                #     xanchor='left',
                #     titleside='right'
                # ),
                line_width=0))

            fig = go.Figure(data=[node_trace2,node_trace3],
                    layout=go.Layout(
                    # title='Graph \'{}\''.format(config['graph']),
                    # titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=0,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), 
                    width=1200,
                    height=1000)
                    )

            # fig.add_trace(go.Heatmap(x = node_x, y = node_y, z = node_z))
            for i in range(0, len(edge_x), 3):
                # print (edge_x[i])
                x1 = edge_x[i + 1]  # arrows' head
                y1 = edge_y[i + 1]  # arrows' head
                x0 = edge_x[i]  # arrows' tail
                y0 = edge_y[i]  # arrows' tail
                # print (x0, y0, x1, y1)

                vert = True
                if x0 != x1:
                    m = (y1 - y0)/(x1 - x0)
                    c = y0 - m * x0
                    vert = False
                
                if vert:
                    yt = y0 + s * np.sign(y1 - y0)
                    yh = y1 - s * np.sign(y1 - y0)
                    xt = x0
                    xh = x1
                else:
                    if y1 == y0:
                        xt = x0 + s * np.sign(x1 - x0)
                        xh = x1 - s * np.sign(x1 - x0)
                        yt = y0
                        yh = y1
                    else:
                        xt = x0 + math.sqrt(s ** 2 / (m ** 2 + 1)) * np.sign(x1 - x0)
                        xh = x1 - math.sqrt(s ** 2 / (m ** 2 + 1)) * np.sign(x1 - x0)
                        yt = m * xt + c
                        yh = m * xh + c
                

                fig.add_annotation(
                    x=xh,  # arrows' head
                    y=yh,  # arrows' head
                    ax=xt,  # arrows' tail
                    ay=yt,  # arrows' tail
                    xref='x',
                    yref='y',
                    axref='x',
                    ayref='y',
                    text='',  # if you want only the arrow
                    showarrow=True,
                    arrowhead=1,
                    arrowsize=2,
                    arrowwidth=1,
                    arrowcolor='black'
                    )
            fig.update_yaxes(
                scaleanchor = "x",
                scaleratio = 1,
            )
            fig.update_layout(title_text='Overshoot frequency', title_x=0.5, titlefont_size = 20, plot_bgcolor = 'rgba(0, 0, 0, 0)')
            fig.to_image(format="png", engine="kaleido")
            fig.write_image('{}/{}_Overshoot_frequency.png'.format(sim_dir, name))
            del fig    
        
    over = dict(zip(nodes,idleness_over))
    non_p_over = []
    pri_nod_over = []
    for i in over.keys():
        if i in priority_nodes:
            pri_nod_over.append(over[i])
        else:
            non_p_over.append(over[i])


    priority_nodes=list(map(int,priority_nodes))
    non_priority_nodes = list(map(int,non_priority_nodes))

    #plotting temporal graph of overshoot
    def temporal_freq():
        plt.figure()
        # sns.set_style('white')
        # sns.set_context(font_scale= 1, rc = {"font.size" : 15, "axes.titlesize" : 20})
        # plt.subplots(figsize = (20, 20))
        # plt.subplots(figsize = (10, 20))
        # plt.subplots_adjust(top= 0.2)
        # sns.set(rc = {'figure.figsize':(20, 100)})
        # sns.relplot(data=non_p, kind='scatter')
        # sns.relplot(data=pri_no, kind='scatter')
        plt.scatter(non_priority_nodes,non_p_over,c="blue")
        plt.scatter(priority_nodes,pri_nod_over,c="red")
        plt.suptitle('Overshoot frequency vs nodes', size = 18, y = 1.02, x = 0.4)
        plt.xticks(rotation = 30)
        plt.ylabel('Node Idleness')

        plt.savefig('{}/{}_Overshoot.png'.format(sim_dir, name), bbox_inches = 'tight')


    idleness_spatial()

    plot_priority_nodes(node_x,node_y,node_x_priority,node_y_priority)

    temporal_freq()
if __name__ == '__main__':
    main(sys.argv[1:])
