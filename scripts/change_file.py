import yaml
import rospkg
import os

def main(folder_name):
    dirname = rospkg.RosPack().get_path('mrpp_sumo')
    config_path = "{}/config/{}".format(dirname,folder_name)
    name_list = folder_name.split("_")


    for i in range(1,37):
        with open('{}/{}_{}_{}_{}.yaml'.format(config_path,name_list[0], name_list[1], i, name_list[-1])) as f:
            list_doc = yaml.safe_load(f)

        # list_doc['depth'] = 3
        list_doc['algo_name'] = "{}_modified_{}".format(name_list[0],name_list[1])
        list_doc['random_string'] = '{}_{}_{}_d{}'.format(list_doc['algo_name'],list_doc['graph'],i,list_doc['depth'])
        if not os.path.exists('{}/config/{}_{}'.format(dirname,list_doc['algo_name'],list_doc['depth'])):
            os.mkdir('{}/config/{}_{}'.format(dirname,list_doc['algo_name'],list_doc['depth']))
        with open('{}/config/{}_{}/{}_d{}_{}.yaml'.format(dirname,list_doc['algo_name'],list_doc['depth'],list_doc['algo_name'],list_doc['depth'],i), "w") as f:
            yaml.dump(list_doc, f)

if __name__ == '__main__':
    folders=['through_basic_1', 'through_basic_3', 'through_basic_5', 'through_FHUM_1', 'through_FHUM_3', 'through_FHUM_5',]
    for i in folders:
        main(i)
