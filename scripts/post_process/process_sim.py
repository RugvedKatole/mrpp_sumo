#!/usr/bin/env python3 

import os
import rospkg
import glob
import sys


def main(string):
    dir_name = rospkg.RosPack().get_path('mrpp_sumo')
    z="_".join(string.split("_")[:-1])
    config_files = glob.glob(dir_name + '/config/{}/{}*.yaml'.format(string,z))
    count = 0
    for conf in config_files:
        path = conf.split('/')
        name = path[-1].split('.')[0]
        print ('Processing {}'.format(name))
        # os.system('python3 {}/scripts/post_process/sim_visualize.py {} grid_5_5'.format(dir_name, name))
        os.system('python3 {}/scripts/post_process/frequency_plots.py {} grid_5_5'.format(dir_name, name))
        count += 1
        print ('{} Done {}'.format(count, conf))

if __name__ == '__main__':
    post=['tpbp_util1_1','tpbp_util1_3','tpbp_util1_5','tpbp_alt1_1','tpbp_alt1_3']
    for i in post:
        main(i)