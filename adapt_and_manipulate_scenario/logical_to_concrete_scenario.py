import json
import time
from pathlib import Path
from adapt_and_manipulate_scenario.sampling_methods.random.random_sampling import random_sampling_func
from adapt_and_manipulate_scenario.sampling_methods.LLM.openai_sampling import openai_sampling_func, first_random_iteration_concrete_scenario_func, previous_random_concrete_value_func_for_LLMs
from adapt_and_manipulate_scenario.sampling_methods.BO.bayesian import bo_sampling_func, previous_random_concrete_value_func

def logi_to_concrete_scenario_converter(input_folder, epoch, intermittent_json_output, logical_scenario_path, iteration_folder, sampling_methods):
    """
    First 5 iterations randomly select the values. 
    From 6 iterations on use LLMs or BO. This helps to converge fast.

    """
    # path definition
    previous_concrete_scenario_path = input_folder / "llms_previous_concrete_scenario.json"
    concrete_scenario_path = iteration_folder/"concrete_scenario.json"

    # For first 5 iterations - use Random Sampling methods.
    if sampling_methods == 'random': 
        concrete_scenario = random_sampling_func(input_folder, epoch, logical_scenario_path, sampling_methods)

        # the json file where the output must be stored 
        with open(concrete_scenario_path, "w") as cs: 
            json.dump(concrete_scenario, cs, indent=4)

    # from 6 iterations - run LLM or BO based on user input
    if sampling_methods == "LLM":
        # for the first 5 epoch, take the random sampling results. 
        if epoch == 1:
            for random_iteration in range(1, 16):
                if random_iteration == 1:
                    previous_concrete_scenario = first_random_iteration_concrete_scenario_func(input_folder)
                else:
                    previous_concrete_scenario = previous_random_concrete_value_func_for_LLMs(random_iteration, input_folder, previous_concrete_scenario, previous_concrete_scenario_path)
                     
        concrete_scenario = openai_sampling_func(epoch, input_folder, previous_concrete_scenario_path, logical_scenario_path, concrete_scenario_path)
   
    elif sampling_methods == "bayesian_optimization":

        if epoch==1:
            previous_random_concrete_value_func(epoch, input_folder, sampling_methods)
        
        concrete_scenario = bo_sampling_func(input_folder, epoch, iteration_folder, logical_scenario_path)
        
        # the json file where the output must be stored 
        with open(concrete_scenario_path, "w") as cs: 
            json.dump(concrete_scenario, cs, indent=4)

    return concrete_scenario, list(concrete_scenario.keys())

if __name__ == "__main__":
    PARENT = Path.cwd().parent 
    input_folder = PARENT / Path("out/test_01").resolve()

    idx=1

    folder_name = "iteration_" + str(idx)
    iteration_folder = input_folder / Path(folder_name).resolve()
    iteration_folder.mkdir(parents=True, exist_ok=True)
    
    logi_out_file = open(input_folder/"logical_scenario.json", "r") 
    logical_scenario = json.load(logi_out_file)
    
    json_out_file = open(input_folder/"intermittent_json.json", "r") 
    intermittent_json_output = json.load(json_out_file)

    logi_to_concrete_scenario_converter(intermittent_json_output, logical_scenario, iteration_folder)


