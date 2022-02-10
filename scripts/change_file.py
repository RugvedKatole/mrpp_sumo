import yaml

for i in range(1,37):
    with open('/home/leo/Thesis/mrpp_sumo/src/config/tpbp_alt1/tpbp_alt1_{}.yaml'.format(i)) as f:
        list_doc = yaml.safe_load(f)

    list_doc['depth'] = 3
    list_doc['random_string'] += '_d{}'.format(str(list_doc['depth'])) 

    with open('/home/leo/Thesis/mrpp_sumo/src/config/through_basic/through_basic_{}_{}.yaml'.format(i,list_doc['depth']), "w") as f:
        yaml.dump(list_doc, f)