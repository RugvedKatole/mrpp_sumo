#!/usr/bin/env python3 

import os
import rospkg
import glob
import sys
from multiprocessing import Pool

def main(string):
    dir_name = rospkg.RosPack().get_path('mrpp_sumo')
    z="_".join(string.split("_")[:-1])
    config_files = glob.glob(dir_name + '/config/{}/{}*.yaml'.format(string,z))
    count = 0
    for conf in config_files:
        path = conf.split('/')
        name = path[-1].split('.')[0]
        print ('Processing {}'.format(name))
        os.system('python3 {}/scripts/post_process/sim_visualize.py {} grid_5_5'.format(dir_name, name))
        os.system('python3 {}/scripts/post_process/frequency_plots.py {} grid_5_5'.format(dir_name, name))
        count += 1
        print ('{} Done {}'.format(count, conf))

if __name__ == '__main__':
    post=['through_FHUM_3','through_FHUM_5']
    for i in post:
        main(i)
    # with Pool(6) as p:
        # p.map(main,post)