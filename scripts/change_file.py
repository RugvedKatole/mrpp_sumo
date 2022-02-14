import yaml
import rospkg
import os

def main(folder_name):
    dirname = rospkg.RosPack().get_path('mrpp_sumo')
    config_path = "{}/config/{}".format(dirname,folder_name)
    name_list = folder_name.split("_")


    for i in range(37,73):
        if len(name_list) < 3:
            # with open('{}/{}_{}_{}_{}.yaml'.format(config_path,name_list[0], name_list[1], i, name_list[-1])) as f:
            with open('{}/{}_{}.yaml'.format(config_path,folder_name, i)) as f:
                list_doc = yaml.safe_load(f)

            list_doc['depth'] = 3
            # if name_list[1]=='final':
                # list_doc['algo_name'] = "{}_modified_basic".format(name_list[0])
            # else:
                # list_doc['algo_name'] = "{}_modified_FHUM".format(name_list[0])
            list_doc['random_string'] = '{}_{}_{}'.format(list_doc['algo_name'],list_doc['graph'],i)
            # if not os.path.exists('{}/config/{}_{}'.format(dirname,list_doc['algo_name'],list_doc['depth'])):
            if not os.path.exists('{}/config/{}'.format(dirname,list_doc['algo_name'])):
                # os.mkdir('{}/config/{}_{}'.format(dirname,list_doc['algo_name'],list_doc['depth']))
                os.mkdir('{}/config/{}'.format(dirname,list_doc['algo_name']))
            # with open('{}/config/{}_{}/{}_d{}_{}.yaml'.format(dirname,list_doc['algo_name'],list_doc['depth'],list_doc['algo_name'],list_doc['depth'],i), "w") as f:
            with open('{}/config/{}/{}_{}.yaml'.format(dirname,list_doc['algo_name'],list_doc['algo_name'],i), "w") as f:
                yaml.dump(list_doc, f)

        else:
            with open('{}/{}_{}_{}_{}.yaml'.format(config_path,name_list[0], name_list[1], i, name_list[-1])) as f:
                list_doc = yaml.safe_load(f)

            # list_doc['depth'] = 3
            list_doc['algo_name'] = "{}_modified_{}".format(name_list[0],name_list[1])
            list_doc['random_string'] = '{}_{}_{}_d{}'.format(list_doc['algo_name'],list_doc['graph'],i,list_doc['depth'])
            if not os.path.exists('{}/config/{}_{}'.format(dirname,list_doc['algo_name'],list_doc['depth'])):
                os.mkdir('{}/config/{}_{}'.format(dirname,list_doc['algo_name'],list_doc['depth']))
            with open('{}/config/{}_{}/{}_{}_{}.yaml'.format(dirname,list_doc['algo_name'],list_doc['depth'],list_doc['algo_name'],list_doc['depth'],i), "w") as f:
                yaml.dump(list_doc, f)

if __name__ == '__main__':
    folders=['through_modified_FHUM_5']
    for i in folders:
        main(i)
