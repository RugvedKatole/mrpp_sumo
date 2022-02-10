import yaml

for i in range(1,37):
    with open('/home/workshop/mrpp_sumo/src/config/tpbp_alt1/tpbp_alt1_{}.yaml'.format(i)) as f:
        list_doc = yaml.safe_load(f)

    list_doc['depth'] = 1
    list_doc['algo_name'] = 'through_FHUM'
    list_doc['random_string'] =  '{}_{}_{}_d{}'.format(list_doc['algo_name'], list_doc['graph'], i, list_doc['depth'])

    with open('//home/workshop/mrpp_sumo/src/config//through_FHUM_{}/through_FHUM_{}_{}.yaml'.format(list_doc['depth'], i, list_doc['depth']), "w") as f:
        yaml.dump(list_doc, f)