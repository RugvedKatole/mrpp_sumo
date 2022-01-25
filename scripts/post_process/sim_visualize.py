# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'


'''
Generate plots and csv files
command: python3 sim_visualize.py 'config_name'
'''
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
pio.kaleido.scope.mathjax = None

def color_map_color(value, cmap_name='Reds', vmin=0, vmax=1):
    # norm = plt.Normalize(vmin, vmax)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap(cmap_name)  # PiYG
    rgb = cmap(norm(abs(value)))[:3]  # will return rgba, we take only first 3 so we get rgb
    color = matplotlib.colors.rgb2hex(rgb)
    return color



def main(param):
    dirname = rospkg.RosPack().get_path('mrpp_sumo')

    #name of the yaml/output files
    name = param[0]
    g = param[1]
    name_list =name.split('_')
    sim_dir = dirname + '/post_process/' + name
    os.mkdir(sim_dir)
    shutil.copy('{}/config/tpbp_final/{}.yaml'.format(dirname,name ), sim_dir)
    shutil.copy('{}/outputs/{}_visits.in'.format(dirname, "_".join(name_list[:-1]) + '_' + g + '_' + name_list[-1]), sim_dir)
    shutil.copy('{}/outputs/{}_command.in'.format(dirname, "_".join(name_list[:-1]) + '_' + g + '_' + name_list[-1]), sim_dir)
    # # shutil.copy('{}/outputs/{}_vehicle.xml'.format(dirdata, name), sim_dir)
    
    #get config and parameters
    with open('{}/config/tpbp_final/{}.yaml'.format(dirname,name), 'r') as f:
        config = yaml.load(f, yaml.FullLoader)
    # print(config)

    graph = nx.read_graphml(dirname + '/graph_ml/{}.graphml'.format(config['graph']))
    nodes = list(graph.nodes())
    edges = [graph[e[0]][e[1]]['name'] for e in list(graph.edges())]
    priority_nodes = config['priority_nodes'].split(' ')
    time_period = config['time_periods'].split(' ')
    n = len(nodes)
    num_bots = int(config['init_bots'])
    sim_length = int(config['sim_length'])
    algo_name = config['algo_name']


    #read visits.in data for a given config
    cols_n = ['time']
    cols_n.extend(nodes)
    df1 = pd.DataFrame(columns = cols_n)
    cols_e = ['time']
    cols_e.extend(edges)
    df2 = pd.DataFrame(columns = cols_e)
    df3 = pd.DataFrame(columns = nodes, index = ['bot_{}'.format(i) for i in range(num_bots)])
    df3 = df3.fillna(0)         
    df4 = pd.DataFrame(columns = cols_n)


    bot_visit_seq = {}
    for bot in range(num_bots):
        bot_visit_seq['bot_{}'.format(bot)] = pd.DataFrame(columns=['time', 'node']) 


    with open('{}/outputs/{}_visits.in'.format(dirname, "_".join(name_list[:-1]) + '_' + g+ '_' + name_list[-1]), 'r') as f:
        robots = {}
        i = 0
        cur_time = 0
        cur_data_n = {}
        cur_data_e = {}
        cur_over_n = {}
        for n in df1.columns:
            cur_data_n[n] = cur_time
        for e in df2.columns:
            cur_data_e[e] = cur_time
        for j in df4.columns:
            cur_over_n[j] = cur_time 

        
        for l in f:
            i += 1
            print(i, cur_time)
            if i % 3 == 1:
                next_time = float(l.strip('\n'))
                while cur_time < next_time:
                    df1 = df1.append(cur_data_n, ignore_index = True)
                    df2 = df2.append(cur_data_e, ignore_index = True)
                    df4 = df4.append(cur_over_n, ignore_index = True)
                    cur_time += 1
                    cur_data_n['time'] = cur_time
                    cur_data_e['time'] = cur_time
                    for n in nodes:
                        cur_data_n[n] += 1
                        cur_over_n[n] = max((cur_data_n[n]-float(time_period[0])),0)

                    
            elif i % 3 == 2:
                cur_nodes = l.strip('\n').split(' ')
                for n in cur_nodes:
                    cur_data_n[n] = 0
                    cur_over_n[n] = 0

            else:
                cur_robots = l.strip('\n').split(' ')
                for r in range(len(cur_robots)):
                    bot_visit_seq[cur_robots[r]] = bot_visit_seq[cur_robots[r]].append({'time': next_time, 'node': cur_nodes[r]}, ignore_index = True)
                    if not cur_robots[r] in robots.keys():
                        robots[cur_robots[r]] = cur_nodes[r]
                        df3[cur_nodes[r]][cur_robots[r]] += 1
                    else:
                        try:
                            cur_data_e[graph[robots[cur_robots[r]]][cur_nodes[r]]['name']] += 1
                            robots[cur_robots[r]] = cur_nodes[r]
                            df3[cur_nodes[r]][cur_robots[r]] += 1
                        except:
                            pass
    df1 = df1.set_index('time')
    df2 = df2.set_index('time')
    df4 = df4.set_index('time')

    df1.to_csv(sim_dir + '/{}_node.csv'.format(name), index = False)
    df2.to_csv(sim_dir + '/{}_edge.csv'.format(name), index = False)
    df3.to_csv(sim_dir + '/{}_bot.csv'.format(name), index = False)
    df4.to_csv(sim_dir + '/{}_Overshoot.csv'.format(name), index = False)
    
    #scatter plot of instantaneous idleness
    plt.figure()
    sns.set_style('white')
    sns.set_context(font_scale= 1, rc = {"font.size" : 15, "axes.titlesize" : 20})
    # plt.subplots(figsize = (10, 20))
    # plt.subplots_adjust(top= 0.2)
    # sns.set(rc = {'figure.figsize':(20, 100)})
    sns.relplot(data= df1.loc[::1000], kind='scatter')
    plt.suptitle('Node Idleness Values vs Time', size = 18, y = 1.02, x = 0.4)
    sns.lineplot(data = df1.iloc[::1000], x = 'time', y = df1.loc[::1000, nodes].mean(axis = 1), legend = False, linewidth = 3)
    plt.xticks(rotation = 30)
    plt.ylabel('Node Idleness')

    plt.savefig('{}/{}_scatter.png'.format(sim_dir, name), bbox_inches='tight')
    # plt.show()


  
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

    # edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888', shape = 'linear'), hoverinfo='none', mode='lines')

    node_x = []
    node_y = []
    node_x_priority= []
    node_y_priority= []
    avg_idle = []
    max_idle = []
    for node in graph.nodes():
        x, y = graph.nodes[node]['x'], graph.nodes[node]['y']
        if node in priority_nodes:
            node_x_priority.append(x)
            node_y_priority.append(y)
        node_x.append(x)
        node_y.append(y)
        avg_idle.append(df1[node].mean())
        max_idle.append(df1[node].max())

    # print('here')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=False,
            color=[],
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

    fig = go.Figure(data=[node_trace],
                layout=go.Layout(
                title='Graph \'{}\''.format(config['graph']),
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
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
                xt = x0 + math.sqrt((s) ** 2 / (m ** 2 + 1)) * np.sign(x1 - x0)
                xh = x1 - math.sqrt((s) ** 2 / (m ** 2 + 1)) * np.sign(x1 - x0)
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
    # print('here_')
    fig.update_layout(title = 'Graph \'{}\''.format(config['graph']), title_x=0.5, titlefont_size = 20, plot_bgcolor = 'rgba(0, 0, 0, 0)')
    fig.to_image(format="png", engine="kaleido")
    fig.write_image('{}/{}_graph.png'.format(sim_dir, name))
    # fig.show()
    # print('here')
    del fig

#Plot Priority nodes on graph
    node_trace = go.Scatter(
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
            color=[],
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
    node_trace1 = go.Scatter(
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

    fig = go.Figure(data=[node_trace,node_trace1],
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
    fig.update_layout(title_text='Priority Node Loctions', title_x=0.5, titlefont_size = 20, plot_bgcolor = 'rgba(0, 0, 0, 0)')
    fig.to_image(format="png", engine="kaleido")
    fig.write_image('/home/leo/Thesis/Test.png')
    # fig.show()
    del fig

    #idleness overshoot
    idleness_over=[]
    for n in df4.columns:
        idleness_over.append(df4[n].value_counts()[1])
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
        fig.write_image('/home/leo/Thesis/mrpp_sumo/src/post_process/tpbp_final_1/tpbp_final_Overshoot_frequency.png')
        del fig     
    
    idleness_spatial()

        

    
    
    
    
    #color map of average idleness
    avg_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Blues',
            reversescale=False,
            color=avg_idle,
            size=2 * d,
            # cmin = 0.,
            # cmax = 200.,
            # opacity = 0.5,
            # showscale = False,
            colorbar=dict(
                thickness=15,
                title='Avg. Node<br>Idleness',
                xanchor='right',
                titleside='top',
            ),
            line_width=2))
    # avg_trace.marker.cmin = 200

    fig = go.Figure(data=[avg_trace],
                layout=go.Layout(
                title='Graph \'{}\''.format(config['graph']),
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=0,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                width=1200,
                height=1000))

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
    fig.update_layout(title_text='Average Node Idleness', title_x=0.5, titlefont_size = 20, plot_bgcolor = 'rgba(0, 0, 0, 0)')
    fig.to_image(format="png", engine="kaleido")
    fig.write_image('{}/{}_avg_idle.png'.format(sim_dir, name))
    # fig.show()
    del fig

    #color map of maximum idleness
    max_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Blues',
            reversescale=False,
            color=max_idle,
            size=2 * d,
            # cmin = 0.,
            # cmax = 300.,
            # opacity = 0.5,
            # showscale = False,
            colorbar=dict(
                thickness=15,
                title='Max. Node<br>Idleness',
                xanchor='right',
                titleside='top'
            ),
            line_width=2))

    fig = go.Figure(data=[max_trace],
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
    fig.update_layout(title_text='Maximum Node Idleness', title_x=0.5, titlefont_size = 20, plot_bgcolor = 'rgba(0, 0, 0, 0)')
    fig.to_image(format="png", engine="kaleido")
    fig.write_image('{}/{}_max_idle.png'.format(sim_dir, name))
    # fig.show()
    del fig


    #color map of probability of next node
    next_edge_count = dict(df2.iloc[-1])
    # next_edge_count.pop('time')
    prob_next_visit = {}
    for n in nodes:
        succ = list(graph.successors(n))
        total_visits = 0
        for k in succ:
            total_visits += next_edge_count[graph[n][k]['name']]
        for k in succ:
            if total_visits == 0:
                total_visits = 1
            prob_next_visit[graph[n][k]['name']] = next_edge_count[graph[n][k]['name']]/total_visits

    # print(prob_next_visit)
    # print(edges)
    max_count = max(list(next_edge_count.values()))
    # print(max_count)
    l = min(50, max([graph[e[0]][e[1]]['length'] for e in graph.edges()]))
    # l = 50
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888', shape = 'linear'), opacity= 0.5, hoverinfo='none', mode='lines')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            # colorscale='#000000',
            reversescale=False,
            color='black',
            size=2 * d,
            # cmin = 0.,
            # cmax = 300.,
            # opacity = 0.5,
            # showscale = False,
            colorbar=dict(
                thickness=15,
                title='Max. Node<br>Idleness',
                xanchor='right',
                titleside='top'
            ),
            line_width=2))

    fig = go.Figure(data=[node_trace, edge_trace],
                layout=go.Layout(
                # title='Graph \'{}\''.format(config['graph']),
                # titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=0,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                width=1200,
                height= 1000)
                )

    for i in range(0, len(edge_x), 3):
        # print (edge_x[i])
        e = edges[i//3]
        len_e  = prob_next_visit[e] * l
        x1 = edge_x[i + 1]  # arrows' head
        y1 = edge_y[i + 1]  # arrows' head
        x0 = edge_x[i]  # arrows' tail
        y0 = edge_y[i]  # arrows' tail
        # print (x0, y0, x1, y1)
        if len_e ** 2 > ((x1 - x0) ** 2 + (y1 - y0) ** 2):
            len_e = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2) - 2 * s

        vert = True
        if x0 != x1:
            m = (y1 - y0)/(x1 - x0)
            c = y0 - m * x0
            vert = False
        
        if vert:
            yt = y0 + s * np.sign(y1 - y0)
            yh = yt + len_e * np.sign(y1 - y0)
            xt = x0
            xh = x1
        else:
            if y1 == y0:
                xt = x0 + s * np.sign(x1 - x0)
                xh = xt + len_e * np.sign(x1 - x0)
                yt = y0
                yh = y1
            else:
                xt = x0 + math.sqrt(s ** 2 / (m ** 2 + 1)) * np.sign(x1 - x0)
                xh = xt + math.sqrt(len_e ** 2 / (m ** 2 + 1)) * np.sign(x1 - x0)
                yt = m * xt + c
                yh = m * xh + c
        
        cval = color_map_color(value = next_edge_count[e], vmin = 0, vmax = max_count)
        # print(cval)
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
            arrowhead=0,
            arrowsize=2,
            arrowwidth=3,
            arrowcolor=cval,
            opacity=0.5
            )
    fig.update_yaxes(
        scaleanchor = "x",
        scaleratio = 1,
    )
    fig.update_layout(title_text = 'Distribution over Neighbours', title_x=0.5, titlefont_size = 20, plot_bgcolor = 'rgba(0, 0, 0, 0)')
    fig.to_image(format="png", engine="kaleido")
    fig.write_image('{}/{}_dist_neigh.png'.format(sim_dir, name))
    # fig.show()
    del fig

    #Bot Histogram

    fig = go.Figure(data = [edge_trace], 
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
    
    total_visits = df3.values.max()
    for i, bot in enumerate(df3.index):
        h = [df3[n][bot]/total_visits for n in nodes]
        fig.add_trace(go.Scatter(
            name = bot,
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                # colorscale='Blues',
                reversescale=False,
                color=color_map_color(value = i, vmin = 0, vmax = len(df3.index) - 1),
                size=2 * d,
                # cmin = 0.,
                # cmax = 300.,
                opacity = h,
                # showscale = False,
                # colorbar=dict(
                #     thickness=15,
                #     title='Max. Node<br>Idleness',
                #     xanchor='right',
                #     titleside='top'
                # ),
                line_width=2)))
    fig.update_yaxes(
        scaleanchor = "x",
        scaleratio = 1,
    )


    fig.update_layout(title_text='Bot Visit Density', title_x=0.5, titlefont_size = 20, plot_bgcolor = 'rgba(0, 0, 0, 0)')
    fig.to_image(format="png", engine="kaleido")
    fig.write_image('{}/{}_bots.png'.format(sim_dir, name))
    # fig.show()

    del fig


    edge_trace = go.Scatter3d(x=edge_x, y=edge_y, z=[0] * len(edge_x), opacity=1, hoverinfo='none', mode='lines')

    node_trace = go.Scatter3d(
        x=node_x, y=node_y,z=[0] * len(nodes),
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
            color=[],
            size=2 * d/10,
            cmin = 0.,
            cmax = 300.,
            # opacity = 0.5,
            # showscale = False,
            colorbar=dict(
                thickness=15,
                title='Max. Node<br>Idleness',
                xanchor='right',
                titleside='top'
            ),
            line_width=2))

    fig = go.Figure(data=[node_trace, edge_trace],
                layout=go.Layout(
                # title='Graph \'{}\''.format(config['graph']),
                # titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=0,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

    for bot in df3.index:
        # print(bot)
        h = [df3[n][bot] for n in nodes]
        fig.add_trace(go.Mesh3d(x = node_x, y = node_y, z = h, opacity= 0.3, name = bot))
    fig.update_traces(alphahull = -1, selector= dict(type = 'mesh3d'))
    fig.write_html('{}/{}_visit_count.html'.format(sim_dir, name))
    # fig.show()

    del fig

    fig = plt.subplot()

    for bot in bot_visit_seq.keys():
        sns.scatterplot(data= bot_visit_seq[bot], y = [int(bot.split('_')[1])] * bot_visit_seq[bot].shape[0], x = 'time', style='node', hue='node', legend = False, palette= 'gist_stern')
    plt.suptitle('Node Visit Sequence vs Time', size = 18, y = 1.02, x = 0.4)

    # sns.lineplot(data = df1.iloc[::100], x = 'time', y = df1.loc[::100, nodes].mean(axis = 1), legend = False, linewidth = 3)
    plt.xticks(rotation = 30)
    fig.set_yticks(list(range(num_bots)))
    fig.set_yticklabels(['bot_{}'.format(bot) for bot in range(0, num_bots)])
    plt.ylabel('Robot ID')
    # plt.show()
    plt.savefig('{}/{}_vist_seq.png'.format(sim_dir, name), bbox_inches='tight')
    # print(num_bots)

    del fig


    #Zoomed In
    fig = plt.subplot()

    for bot in bot_visit_seq.keys():
        mask = bot_visit_seq[bot]['time'] >= 195000
        sns.scatterplot(data= bot_visit_seq[bot][mask], y = [int(bot.split('_')[1])] * bot_visit_seq[bot][mask].shape[0], x = 'time', style='node', hue='node', legend = False, palette= 'gist_stern')
    plt.suptitle('Node Visit Sequence vs Time', size = 18, y = 1.02, x = 0.4)

    # sns.lineplot(data = df1.iloc[::100], x = 'time', y = df1.loc[::100, nodes].mean(axis = 1), legend = False, linewidth = 3)
    plt.xticks(rotation = 30)
    fig.set_yticks(list(range(num_bots)))
    fig.set_yticklabels(['bot_{}'.format(bot) for bot in range(0, num_bots)])
    plt.ylabel('Robot ID')
    # plt.show()
    plt.savefig('{}/{}_last_seq.png'.format(sim_dir, name), bbox_inches='tight')
    # print(num_bots)

    del fig


    for bot in bot_visit_seq.keys():
        plt.figure()
        plt.subplots(figsize = (20, 20))
        sns.scatterplot(data= bot_visit_seq[bot], y = 'node', x = 'time', style='node', legend = False)
        plt.suptitle('Node Visit Instance vs Time ({})'.format(bot), size = 36, x = 0.4, y=0.98)

        plt.xticks(rotation = 30)
        plt.yticks(rotation = 30)
        plt.ylabel('Node ID')
        plt.savefig('{}/{}_scatter.png'.format(sim_dir, bot), bbox_inches = 'tight')
    # print ('here')


    #Overshoot temporal plot
    over = dict(zip(nodes,idleness_over))
    non_p_over = []
    pri_nod_over = []
    for i in over.keys():
        if i in priority_nodes:
            pri_nod_over.append(over[i])
        else:
            non_p_over.append(over[i])

    non_priority_nodes = [u for u in graph.nodes if u not in priority_nodes]
    priority_nodes=list(map(int,priority_nodes))
    non_priority_nodes = list(map(int,non_priority_nodes))


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

    #Adding to master data set

    df = pd.read_csv(dirname + '/tpbp.csv')
    to_add = {}
    to_add = config.copy()
    to_add['max_idle'] = np.max(max_idle)
    to_add['avg_idle'] = np.mean(avg_idle)
    for col in to_add.keys():
        if not col in df.columns:
            df.reindex(columns = df.columns.tolist() + [col])
    if not to_add['random_string'] in map(str, df['random_string']):
        df = df.append(to_add, ignore_index = True)
    df.to_csv(dirname + '/tpbp.csv', index = False)
    del df1, df2, df3, df




if __name__ == '__main__':
    main(sys.argv[1:])