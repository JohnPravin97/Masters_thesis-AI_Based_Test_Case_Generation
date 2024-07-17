import random
import json 
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel
import os
import numpy as np
import time
from pathlib import Path

PARENT = Path.cwd().parent 
 
def previous_random_concrete_value_func(epoch, input_folder, sampling_methods):
    for epoch in range(1, 16):
        bo_list = []
        iteration_name = "random/iteration_"+str(epoch)+"/concrete_scenario.json"
        random_sampling_iteration_folder = input_folder / Path(iteration_name)
        with open(random_sampling_iteration_folder, "r") as ls:
            previous_concrete_scenario =  json.load(ls)

        # Random Sampling methods. 
        for first_key in list(previous_concrete_scenario.keys()):
            for second_key, _ in previous_concrete_scenario[first_key].items():
                for third_key, third_value in previous_concrete_scenario[first_key][second_key].items():
                    if isinstance(third_value, str):
                        if previous_concrete_scenario[first_key][second_key][third_key] not in ["time", "distance", "rain"]:
                            bo_list.append(float(previous_concrete_scenario[first_key][second_key][third_key]))

                    elif isinstance(third_value, dict):
                        for fourth_key, fourth_value in previous_concrete_scenario[first_key][second_key][third_key].items():
                            if isinstance(fourth_value, str):
                                # print(fourth_key, fourth_value)
                                if previous_concrete_scenario[first_key][second_key][third_key][fourth_key] not in ["time", "distance", "rain"]:
                                    bo_list.append(float(previous_concrete_scenario[first_key][second_key][third_key][fourth_key]))

                            elif isinstance(fourth_value, dict):
                                for fifth_key, fifth_value in previous_concrete_scenario[first_key][second_key][third_key][fourth_key].items():
                                    if isinstance(fifth_value, str):
                                        if previous_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key] not in ["time", "distance", "rain"]:
                                            bo_list.append(float(previous_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key]))

                                    # not needed but just in case
                                    elif isinstance(fifth_value, dict):
                                        for sixth_key, sixth_value in previous_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key].items():
                                            if isinstance(sixth_value, str):     
                                                if previous_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key][sixth_key] not in ["time", "distance", "rain"]:
                                                    bo_list.append(float(previous_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key][sixth_key]))
        
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

# randomly select a concrete value from the range of logical values
def random_test_parameter_func_for_bo(iteration_folder, logical_scenario_path, number_of_options=50):
    
    with open(logical_scenario_path, "r") as ls:
        logical_scenario =  json.load(ls)

    for option in range(number_of_options):
        bo_sample_list = []
        # concrete_scenario = logical_scenario.copy()
        # Random Sampling methods. 
        for first_key in list(logical_scenario.keys()):
            for second_key, _ in logical_scenario[first_key].items():
                for third_key, third_value in logical_scenario[first_key][second_key].items():
                    if isinstance(third_value, list):
                        # concrete_scenario[first_key][second_key][third_key] = str(round(random.uniform(third_value[0], third_value[1]), 2))
                        bo_sample_list.append(float(random.randint(int(third_value[0]), int(third_value[1]))))
                    
                    elif isinstance(third_value, dict):
                        for fourth_key, fourth_value in logical_scenario[first_key][second_key][third_key].items():
                            if isinstance(fourth_value, list):
                                # print(fourth_key, fourth_value)
                                # concrete_scenario[first_key][second_key][third_key][fourth_key] = str(round(random.uniform(fourth_value[0], fourth_value[1]), 2))
                                bo_sample_list.append(float(random.randint(int(fourth_value[0]), int(fourth_value[1]))))

                            elif isinstance(fourth_value, dict):
                                for fifth_key, fifth_value in logical_scenario[first_key][second_key][third_key][fourth_key].items():
                                    if isinstance(fifth_value, list):
                                        # concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key] = str(random.randint(fifth_value[0], int(fifth_value[1])))
                                        bo_sample_list.append(float(random.randint(int(fifth_value[0]), int(fifth_value[1]))))
                                    
                                    # not needed but just in case
                                    elif isinstance(fifth_value, dict):
                                        for sixth_key, sixth_value in logical_scenario[first_key][second_key][third_key][fourth_key][fifth_key].items():
                                            if isinstance(sixth_value, list):
                                                # concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key][sixth_key] = str(round(random.randint(sixth_value[0], sixth_value[1]), 2))  
                                                bo_sample_list.append(float(random.randint(int(sixth_value[0]), int(sixth_value[1]))))          
        
        file_path = iteration_folder/"bayesian_sample_concrete_values.json"

        if os.path.exists(file_path) == False:
            obj = {"selection_values_"+str(option): bo_sample_list}
            with open(file_path, "w") as savefile:
                json.dump(obj, savefile)

        else:
            with open(file_path, "r") as json_file:
                obj2 = {"selection_values_"+str(option): bo_sample_list}
                readObj = json.load(json_file)
                readObj.update(obj2)
            
            with open(file_path, "w") as json_file:
                json.dump(readObj, json_file)

def bo_setup(input_folder, epoch, iteration_folder):
    
    start = time.time()
    samples_file_path = iteration_folder/"bayesian_sample_concrete_values.json"
    eval_outputpath = PARENT / Path(f"evaluation/logi_2_concrete/bayesian_optimization/{input_folder.stem}_bo_sample_time_taken.txt").resolve()

    # read the previous parameters
    with open(input_folder/"bo_previous_concrete_scenario.json", "r") as param:
        parameters = np.array(list(json.load(param).values()))

    # read the options parameter to pick one using bayesian optimization
    with open(samples_file_path, "r") as json_file:
        sample_parameters_x = np.array(list(json.load(json_file).values()))
    
    with open(input_folder/"test_score.json", "r") as json_file:
        scores = np.array(json.load(json_file)["test_score"])
        final_scores = np.expand_dims(scores, axis=1)
        print(scores)
        # scores = np.array([[45], [98], [18], [81], [66], [45], [98], [18], [81], [66], [45], [98], [18], [81], [66]]) # 

    # bayesian optimization
    kernel = ConstantKernel(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e3))
    gp = GaussianProcessRegressor(kernel, n_restarts_optimizer=5000)
    gp.fit(parameters, final_scores)

    y_mean, y_std = gp.predict(sample_parameters_x, return_std=True)
    # y_std = y_std.reshape((-1, 1))
    y_max = np.max(final_scores)

    # aggregation function
    expected_improvement = (y_mean + 1.96 * y_std) - y_max
    max_index = expected_improvement.argmax()

    next_parameter = sample_parameters_x[max_index].tolist()

    # save the next parameter to the previous sampling json file
    with open(input_folder/"bo_previous_concrete_scenario.json", "r") as json_file:
        obj2 = {"previous_sampling_"+str(15 + epoch): next_parameter}
        readObj = json.load(json_file)
        readObj.update(obj2)
    
    with open(input_folder/"bo_previous_concrete_scenario.json", "w") as json_file:
        json.dump(readObj, json_file)
    
    end = time.time()
    
    with open(eval_outputpath, "a+") as eval_file:
        output_iteration = f"Test_Number= {input_folder.stem.split('_')[-1]},\n Iterations = {epoch}, Technique_Used = 'bayesian_optimization', Time_Taken = {end-start}s \n\n"
        eval_file.write(output_iteration)

    print("Bayesian optimization model took",end-start,"seconds for sampling next value")

def bo_test_case_generation(input_folder, epoch, logical_scenario_path):
    with open(logical_scenario_path, "r") as ls:
        logical_scenario =  json.load(ls)

    with open(input_folder/"bo_previous_concrete_scenario.json", "r") as json_file:
        concrete_values = json.load(json_file).get("previous_sampling_"+str(15+epoch), None)

    if concrete_values is None:
        raise Exception("something is wrong in concrete value test case generation")

    # copy the concrete scenario from the logical scenario for the conversion
    concrete_scenario = logical_scenario.copy()

    concrete_values = iter(concrete_values)

    for first_key in list(logical_scenario.keys()):
        for second_key, _ in logical_scenario[first_key].items():
            for third_key, third_value in logical_scenario[first_key][second_key].items():
                if isinstance(third_value, list):
                    concrete_scenario[first_key][second_key][third_key] = str(next(concrete_values))
                    
                
                elif isinstance(third_value, dict):
                    for fourth_key, fourth_value in logical_scenario[first_key][second_key][third_key].items():
                        if isinstance(fourth_value, list):
                            concrete_scenario[first_key][second_key][third_key][fourth_key] = str(next(concrete_values))
                            

                        elif isinstance(fourth_value, dict):
                            for fifth_key, fifth_value in logical_scenario[first_key][second_key][third_key][fourth_key].items():
                                if isinstance(fifth_value, list):
                                    concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key] = str(next(concrete_values))
                                    
                                
                                # not needed but just in case
                                elif isinstance(fifth_value, dict):
                                    for sixth_key, sixth_value in logical_scenario[first_key][second_key][third_key][fourth_key][fifth_key].items():
                                        if isinstance(sixth_value, list):
                                            concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key][sixth_key] = str(next(concrete_values))
    return concrete_scenario
                    
def bo_sampling_func(input_folder, epoch, iteration_folder, logical_scenario_path):

    # randomly select 50 options within the range
    random_test_parameter_func_for_bo(iteration_folder, logical_scenario_path)

    # set up the bayesian optimization and select the best parameters
    bo_setup(input_folder, epoch, iteration_folder)

    # write it in the 
    concrete_scenario = bo_test_case_generation(input_folder, epoch, logical_scenario_path)

    return concrete_scenario

    

