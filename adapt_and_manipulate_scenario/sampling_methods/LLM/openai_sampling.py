import json
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
import os
import time
import numpy as np

# Load environment variables from .env file
load_dotenv()

OPEN_AI_API_KEY = os.environ['OPEN_AI_API']

PARENT = Path.cwd().parent


def first_random_iteration_concrete_scenario_func(input_folder):
    iteration_name = "random/iteration_"+str(1)+"/concrete_scenario.json"
    concrete_scenario_path = input_folder / Path(iteration_name)
    
    with open(concrete_scenario_path, "r") as cs:
        first_concrete_scenario = json.load(cs)

    overall_concrete_scenario = first_concrete_scenario.copy()
    for first_key in list(first_concrete_scenario.keys()):
        for second_key, _ in first_concrete_scenario[first_key].items():
            for third_key, third_value in first_concrete_scenario[first_key][second_key].items():
                if isinstance(third_value, str):
                    overall_concrete_scenario[first_key][second_key][third_key] = [first_concrete_scenario[first_key][second_key][third_key]]

                elif isinstance(third_value, dict):
                    for fourth_key, fourth_value in first_concrete_scenario[first_key][second_key][third_key].items():
                        if isinstance(fourth_value, str):
                            # print(fourth_key, fourth_value)
                            overall_concrete_scenario[first_key][second_key][third_key][fourth_key] = [first_concrete_scenario[first_key][second_key][third_key][fourth_key]]

                        elif isinstance(fourth_value, dict):
                            for fifth_key, fifth_value in first_concrete_scenario[first_key][second_key][third_key][fourth_key].items():
                                if isinstance(fifth_value, str):
                                    overall_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key] = [first_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key]]
                                # not needed but just in case
                                elif isinstance(fifth_value, dict):
                                    for sixth_key, sixth_value in first_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key].items():
                                        if isinstance(sixth_value, str):
                                            overall_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key][sixth_key] = [first_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key]]       
    return overall_concrete_scenario

def previous_random_concrete_value_func_for_LLMs(epoch, input_folder, overall_concrete_scenario, previous_concrete_scenario_path):
    iteration_name = "random/iteration_"+str(epoch)+"/concrete_scenario.json"
    random_sampling_iteration_folder = input_folder / Path(iteration_name)
    with open(random_sampling_iteration_folder, "r") as cs:
        concrete_scenario = json.load(cs)
    
    for first_key in list(concrete_scenario.keys()):
        for second_key, _ in concrete_scenario[first_key].items():
            for third_key, third_value in concrete_scenario[first_key][second_key].items():
                if isinstance(third_value, str):
                    overall_concrete_scenario[first_key][second_key][third_key].append(concrete_scenario[first_key][second_key][third_key])

                elif isinstance(third_value, dict):
                    for fourth_key, fourth_value in concrete_scenario[first_key][second_key][third_key].items():
                        if isinstance(fourth_value, str):
                            # print(fourth_key, fourth_value)
                            overall_concrete_scenario[first_key][second_key][third_key][fourth_key].append(concrete_scenario[first_key][second_key][third_key][fourth_key])

                        elif isinstance(fourth_value, dict):
                            for fifth_key, fifth_value in concrete_scenario[first_key][second_key][third_key][fourth_key].items():
                                if isinstance(fifth_value, str):
                                    overall_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key].append(concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key])
                                # not needed but just in case
                                elif isinstance(fifth_value, dict):
                                    for sixth_key, sixth_value in concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key].items():
                                        if isinstance(sixth_value, str):
                                            overall_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key][sixth_key].append(concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key])     
    
    # the json file that holds the previous samples
    # overwrite the updated concrete scenario with the old one
    with open(previous_concrete_scenario_path, "w") as cs: 
        json.dump(overall_concrete_scenario, cs, indent=4)

    return overall_concrete_scenario

def LLMs_test_case_generation(concrete_scenario_json_out, previous_concrete_scenario_path):

    with open(previous_concrete_scenario_path, "r") as ls:
        overall_concrete_scenario =  json.load(ls)
    
    for first_key in list(concrete_scenario_json_out.keys()):
        for second_key, _ in concrete_scenario_json_out[first_key].items():
            for third_key, third_value in concrete_scenario_json_out[first_key][second_key].items():
                if isinstance(third_value, str):
                    overall_concrete_scenario[first_key][second_key][third_key].append(concrete_scenario_json_out[first_key][second_key][third_key])

                elif isinstance(third_value, dict):
                    for fourth_key, fourth_value in concrete_scenario_json_out[first_key][second_key][third_key].items():
                        if isinstance(fourth_value, str):
                            # print(fourth_key, fourth_value)
                            overall_concrete_scenario[first_key][second_key][third_key][fourth_key].append(concrete_scenario_json_out[first_key][second_key][third_key][fourth_key])

                        elif isinstance(fourth_value, dict):
                            for fifth_key, fifth_value in concrete_scenario_json_out[first_key][second_key][third_key][fourth_key].items():
                                if isinstance(fifth_value, str):
                                    overall_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key].append(concrete_scenario_json_out[first_key][second_key][third_key][fourth_key][fifth_key])
                                # not needed but just in case
                                elif isinstance(fifth_value, dict):
                                    for sixth_key, sixth_value in concrete_scenario_json_out[first_key][second_key][third_key][fourth_key][fifth_key].items():
                                        if isinstance(sixth_value, str):
                                            overall_concrete_scenario[first_key][second_key][third_key][fourth_key][fifth_key][sixth_key].append(concrete_scenario_json_out[first_key][second_key][third_key][fourth_key][fifth_key])     
    
    # the json file that holds the previous samples
    # overwrite the updated concrete scenario with the old one
    with open(previous_concrete_scenario_path, "w") as cs: 
        json.dump(overall_concrete_scenario, cs, indent=4)

def openai_sampling_func(epoch, input_folder, previous_concrete_scenario_path, logical_scenario_path, concrete_scenario_path):

    ## Prompt for sampling
    prompt_filepath = PARENT / Path("adapt_and_manipulate_scenario/sampling_methods/LLM/prompts/open_ai_sampling_prompt.txt").resolve()

    role_prompt_filepath = PARENT / Path("adapt_and_manipulate_scenario/sampling_methods/LLM/prompts/open_ai_sampling_prompt_role.txt").resolve()
    
    eval_outputpath = PARENT / Path(f"evaluation/logi_2_concrete/LLM/{input_folder.stem}_llm_sample_time_taken.txt").resolve()

    # take the prompt from the eval folder
    with open(prompt_filepath, "r") as p:
        prompt = p.read()

        # take the prompt from the eval folder
    with open(role_prompt_filepath, "r") as role:
        role_prompt = role.read()

    # read the old concrete scenario
    with open(previous_concrete_scenario_path, "r") as cs: 
        previous_concrete_scenario = json.load(cs)
    
    with open(logical_scenario_path, "r") as ls:
        logical_scenario =  json.load(ls)

    # test scores
    with open(input_folder/"llms_test_score.json", "r") as json_file:
        scores = json.load(json_file)["test_score"]
        # final_scores = np.expand_dims(scores, axis=1)
        print(scores)

    final_prompt = role_prompt +  "##Context:\n" + str(logical_scenario) + prompt + "\n##Previous_iterations:\n" + str(previous_concrete_scenario) + "\n##Previous_results: "+ str(scores) +"\n"# TODO add previous results

    user_text = "you can select the next value for each parameter to get the result"
    
    ## OpenAI
    start = time.time()
    client = OpenAI(api_key = OPEN_AI_API_KEY)

    output = client.chat.completions.create(
    model="gpt-4-0125-preview",
    messages=[
        {"role": "system", "content": final_prompt},
        {"role": "user", "content": user_text}
    ], 
        max_tokens=2000
    )
    # print(output.choices[0].message.content)
    try: 
        concrete_scenario_json_out = json.loads(output.choices[0].message.content)
    except:
        try: 
            concrete_scenario_json_out = json.loads(output.choices[0].message.content.strip("```"))
        except:
            try:
                concrete_scenario_json_out = json.loads(output.choices[0].message.content.strip("```").split("json")[-1])
            except:
                try: 
                    concrete_scenario_json_out = json.loads(output.choices[0].message.content.split("```json")[-1]).split("```")[0]
                except:
                    raise Exception("Something wrong with - " + output.choices[0].message.content)
    

    end = time.time()
    with open(eval_outputpath, "a+") as eval_file:
        output_iteration = f"Test_Number= {input_folder.stem.split('_')[-1]},\n Iterations = {epoch}, Technique_Used = 'LLM', Time_Taken = {end-start}s \n\n"
        eval_file.write(output_iteration)

    print("OpenAI model took",end-start,"seconds for sampling next value")

    if "comments" in concrete_scenario_json_out.keys():
        del concrete_scenario_json_out["comments"]
    
    elif "comment" in concrete_scenario_json_out.keys():
        del concrete_scenario_json_out["comment"]
        
    # the json file where the output must be stored 
    with open(concrete_scenario_path, "w") as cs: 
        json.dump(concrete_scenario_json_out, cs, indent=4)
     
    # add it to the previous llms generated json file. 
    LLMs_test_case_generation(concrete_scenario_json_out, previous_concrete_scenario_path)

    return concrete_scenario_json_out

    
