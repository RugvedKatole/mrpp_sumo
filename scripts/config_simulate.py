#!/bin/usr/env python3

import configparser as CP
import os
import rospkg
import glob

dir_name = rospkg.RosPack().get_path('mrpp_sumo')
config_files = glob.glob(dir_name + '/config/qsp*.yaml')
count = 0
for conf in config_files:
    name = conf.split('/')[-1].split('.')[0]
    # os.system('xterm -e "{}/tpbp.sh" {}'.format(dir_name, conf))
    os.system('python3 {}/scripts/algorithms/offline_algos/ant_q_tsp.py {}'.format(dir_name, conf))
    os.system('ffmpeg -framerate 20 -i {a}/outputs/{b}/img_%d.png -c:v libx264 -pix_fmt yuv420p {a}/outputs/{b}.mp4'.format_map({'a': dir_name, 'b': name}))
    count += 1
    print ('{} Done {}'.format(count, conf))
