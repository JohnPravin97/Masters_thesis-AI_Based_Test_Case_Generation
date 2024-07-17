import random
import json 
import numpy as np
import os

# randomly select a concrete value from the range of logical values
def random_sampling_func(input_folder, epoch, logical_scenario_path, sampling_methods):
    bo_list = []

    with open(logical_scenario_path, "r") as ls:
        logical_scenario =  json.load(ls)

    concrete_scenario = logical_scenario.copy()
    # Random Sampling methods. 
    for first_key in list(logical_scenario.keys()):
        for second_key, _ in logical_scenario[first_key].items():
            for third_key, third_value in logical_scenario[first_key][second_key].items():
                if isinstance(third_value, list):
                    a = float(random.randint(int(third_value[0]), int(third_value[1])))
                    concrete_scenario[first_key][second_key][third_key] = str(a)
                    bo_list.append(a)

                elif isinstance(third_value, dict):
                    for fourth_key, fourth_value in logical_scenario[first_key][second_key][third_key].items():
                        if isinstance(fourth_value, list):
                            # print(fourth_key, fourth_value)
                            b = float(random.randint(int(fourth_value[0]), int(fourth_value[1])))
                            concrete_scenario[first_key][second_key][third_key][fourth_key] = str(b)
                            bo_list.append(b)

                        elif isinstance(fourth_value, dict):
                            for fifth_key, fifth_value in logical_scenario[first_key][second_key][third_key][fourth_key].items():
                                if isinstance(fifth_value, list):
                                    c = float(random.randint(int(fifth_value[0]), int(fifth_value[1])))
                                    concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key] = str(c)
                                    bo_list.append(c)

                                # not needed but just in case
                                elif isinstance(fifth_value, dict):
                                    for sixth_key, sixth_value in logical_scenario[first_key][second_key][third_key][fourth_key][fifth_key].items():
                                        if isinstance(sixth_value, list):
                                            d = float(random.randint(int(sixth_value[0]), int(sixth_value[1])))
                                            concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key][sixth_key] = str(d)          
                                            bo_list.append(d) 
    
    # used for bayesian optimization to store the previous concrete values from random
    if sampling_methods == "bayesian_optimization":
        jsonFilePath = input_folder/"bo_previous_concrete_scenario.json"
        if os.path.exists(jsonFilePath) == False:
            obj = {"previous_sampling_"+str(epoch): bo_list}
            with open(jsonFilePath, "w") as savefile:
                json.dump(obj, savefile)

        else:
            with open(jsonFilePath, "r") as json_file:
                obj2 = {"previous_sampling_"+str(epoch): bo_list}
                readObj = json.load(json_file)
                readObj.update(obj2)
            
            with open(jsonFilePath, "w") as json_file:
                json.dump(readObj, json_file)

    return concrete_scenario 

