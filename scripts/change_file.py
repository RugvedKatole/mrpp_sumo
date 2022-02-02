import yaml

for i in range(1,37):
    with open('/home/workshop/mrpp_sumo/src/config/tpbp_alt1/tpbp_alt1_{}.yaml'.format(i)) as f:
        list_doc = yaml.safe_load(f)

    list_doc['depth'] = 3
    list_doc['depth'] += '_{}'.format(list_doc['depth'])  

    with open('/home/workshop/mrpp_sumo/src/config/tpbp_alt1_3/tpbp_alt1_{}_3.yaml'.format(i), "w") as f:
        yaml.dump(list_doc, f)