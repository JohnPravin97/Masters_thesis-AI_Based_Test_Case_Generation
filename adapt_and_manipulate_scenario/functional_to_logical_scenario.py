"""
input - functional scenario
output - logical scenario
"""
from dotenv import load_dotenv
import os
from openai import OpenAI
import time
from pathlib import Path
import json 
import random
import shutil
# from lxml import etree
from adapt_and_manipulate_scenario.utils.road_len_calculator import RoadLenCalculate
from gpt4all import GPT4All


# Load environment variables from .env file
load_dotenv()

OPEN_AI_API_KEY = os.environ['OPEN_AI_API']

PARENT = Path.cwd().parent

class Func2LogiConvertor:
    def __init__(self):
        pass

    def openai_setup(self, prompt, user_text):
        ## OpenAI
        start = time.time()
        client = OpenAI(api_key = OPEN_AI_API_KEY)

        ## uncomment for gpt 4
        output = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text}
        ], 
            max_tokens=200
        )

        ## uncomment for gpt3.5
        # output = client.chat.completions.create(
        # model="gpt-3.5-turbo-0125",
        # messages=[
        #     {"role": "system", "content": prompt},
        #     {"role": "user", "content": user_text}
        # ], 
        #     max_tokens=200
        # )

        # print(output.choices[0].message.content)
        try: 
            json_out = json.loads(output.choices[0].message.content)
        except:
            try: 
                json_out = json.loads(output.choices[0].message.content.strip("```"))
            except:
                try:
                    json_out = json.loads(output.choices[0].message.content.strip("```").split("json")[-1])
                except:
                    raise Exception("Something wrong with - " + output.choices[0].message.content)
        

        end = time.time()
        print("OpenAI model took",end-start,"seconds")

        return json_out

    def mistral_opensource_setup(self, prompt, user_text):
        start = time.time()

        # "gpt4all-falcon-newbpe-q4_0.gguf" - Falcon model
        # for cpu
        model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")

        # for gpu
        model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf", device="gpu")


        # for gpu
        final_prompt = prompt +"Input:"+user_text+"Output:"
        output = model.generate(prompt= final_prompt, max_tokens=1000)
        print(output)
        try: 
            json_out = json.loads(output)
        except:
            try: 
                json_out = json.loads(output.split('"""')[0])
            except:
                try:
                    json_out=json.loads(output.replace("\\_", "_"))
                except:
                    try: 
                        json_out=json.loads(output.split("Input")[0])
                    except:
                        raise Exception("Something wrong with - " + output)
        

        end = time.time()
        print("Mistral-7B opensource model took",end-start,"seconds")

        return json_out

    def orca2_opensource_setup(self, prompt, user_text):
        start = time.time()

        # orca 2 -7B - "orca-2-7b.Q4_0.gguf" - want to use 7B - replace this model name down. 

        # orca2 -13B
        ## for cpu
        # model = GPT4All("orca-2-13b.Q4_0.gguf")

        ## for gpu
        model = GPT4All("orca-2-13b.Q4_0.gguf", device="gpu")

        final_prompt = prompt +"Input:"+user_text+"Output:"
        output = model.generate(prompt = final_prompt, max_tokens=1000)
        print(output)
        try: 
            json_out = json.loads(output)
        except:
            try: 
                json_out = json.loads(output.split('"""')[0])
            except:
                try:
                    json_out=json.loads(output.replace("\\_", "_"))
                except:
                    raise Exception("Something wrong with - " + output)
        

        end = time.time()
        print("Orca2 opensource model took",end-start,"seconds")

        return json_out
    
    def llama3_opensource_setup(self, prompt, user_text):
        start = time.time()

        # LLama3 -8B - "Meta-Llama-3-8B-Instruct.Q4_0.gguf"

        # LLama3 -8B
        ## for cpu
        model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

        ## for gpu
        # model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", device="gpu")

        final_prompt = prompt +"\n<|start_header_id|>user<|end_header_id|>\n"+user_text+"\n<|eot_id|>"
        output = model.generate(prompt = final_prompt, max_tokens=1000)
        # print(output)
        try: 
            json_out = json.loads(output.split("<|start_header_id|>assistant<|end_header_id|>")[1].split("<|eot_id|>")[0])
        except:
            try: 
                json_out = json.loads(output.split("<|assistant|>")[1].split("<|eot_id|>")[0])
            except:
                try: 
                    json_out = json.loads(output.split("<|assistant_id|>")[1].split("<|eot_id|>")[0])
                except: 
                    raise Exception("Something wrong with - " + output)
        

        end = time.time()
        print("Llama 3 opensource model took",end-start,"seconds")

        return json_out
    
    def wizardlm_opensource_setup(self, prompt, user_text):
        start = time.time()

        # "gpt4all-falcon-newbpe-q4_0.gguf" - Falcon model
        ## for cpu
        # model = GPT4All("wizardlm-13b-v1.2.Q4_0.gguf")

        ## for gpu
        model = GPT4All("wizardlm-13b-v1.2.Q4_0.gguf", device='gpu')

        final_prompt = prompt +"USER:"+ user_text +"ASSISTANT:"
        output = model.generate(prompt=final_prompt, max_tokens=1000)

        try: 
            json_out = json.loads(output)
        except:
            try: 
                json_out = json.loads(output.split('"""')[0])
            except:
                raise Exception("Something wrong with Json output")
        
        end = time.time()
        print("Wizard LM opensource model took",end-start,"seconds to convert func to json")

        return json_out

    def _choose_scenario_from_generated_scenario(self, json_output, store_path):

        ## copy the scenario from the generate scenario to the test folder
        scenario_information = json_output["map"]+ "__" + json_output["scenario"] + "__" + json_output["road"]

        path = Path("generate_scenario/output_scenarios") / scenario_information

        scenario_path = PARENT / path.resolve()

        scenario_list = []
        for scenario in scenario_path.glob("*.xosc"):
            scenario_list.append(scenario)

        selected_scenario = str(random.choice(scenario_list))

        # uncomment if the scenario already exist
        # selected_scenario = str(next(store_path.glob("*.xosc")))

        # calculate the road max values
        rlc = RoadLenCalculate(selected_scenario, scenario_information)
        road_len_dic = rlc.run()
    
        # TODO rename the name
        # shutil.copy(selected_scenario, store_path) 

        return road_len_dic

    def _func_to_json_converter(self, user_text, store_path, llm_selector):
        
        ## OpenAI
        if llm_selector == "OpenAI":
            prompt_path =  PARENT / Path("adapt_and_manipulate_scenario/functional_to_json_llms/prompts/open_ai_prompt.txt").resolve()

            # take the prompt from the functional_to_json_llms folder
            with open(prompt_path, "r") as p:
                prompt = p.read()
            
            json_output = self.openai_setup(prompt, user_text)

        ## OpenSource LLM
        # # https://gpt4all.io/index.html
        elif llm_selector == "MistralAI":
            prompt_path =  PARENT / Path("adapt_and_manipulate_scenario/functional_to_json_llms/prompts/mistral_prompt.txt").resolve()

            # take the prompt from the functional_to_json_llms folder
            with open(prompt_path, "r") as p:
                prompt = p.read()
            
            json_output = self.mistral_opensource_setup(prompt, user_text)
        
        elif llm_selector == "WizardLM":
            prompt_path =  PARENT / Path("adapt_and_manipulate_scenario/functional_to_json_llms/prompts/wizardlm_prompt.txt").resolve()

            # print(str(prompt_path))

            # take the prompt from the functional_to_json_llms folder
            with open(prompt_path, "r") as p:
                prompt = p.read()
            
            json_output = self.wizardlm_opensource_setup(prompt, user_text)

        elif llm_selector == "Llama-3":
            prompt_path =  PARENT / Path("adapt_and_manipulate_scenario/functional_to_json_llms/prompts/llama3_prompt.txt").resolve()

            # print(str(prompt_path))

            # take the prompt from the functional_to_json_llms folder
            with open(prompt_path, "r") as p:
                prompt = p.read()
            
            json_output = self.llama3_opensource_setup(prompt, user_text)

        # the json file where the output must be stored 
        out_file = open(store_path/"intermittent_json.json", "w") 
        json.dump(json_output, out_file, indent=4)

        return json_output

    def _json_to_logi_converter(self, json_output, road_len_dic, store_path):
        number_in_words = ["one", "two", "three", "four"]
        logical_scenario = {"weather": {}}

        logical_scenario_template_path = PARENT / Path("adapt_and_manipulate_scenario/templates/logical_scenario_template.json").resolve()
        
        logical_scenario_template = json.load(open(logical_scenario_template_path, "r"))
        # json_output["actors"]

        for actor, value in json_output["actors"].items():
            if "hero_vehicle" in actor and value != 0:
                logical_scenario["hero"] = logical_scenario_template["hero"]
                if logical_scenario["hero"].get("RoutingAction", 0) != 0:
                    logical_scenario["hero"]["RoutingAction"]["s"][1] = float(road_len_dic["hero"]["RoutingAction"]["max_length"])
            
            elif "adversary_vehicle" in actor and value != 0:
                logical_scenario["adversary"] = logical_scenario_template["adversary"]
                logical_scenario["adversary"]["LanePosition"]["s"][1] = float(road_len_dic["adversary"]["LanePosition"]["max_length"])
            
            elif "bicycle" in actor and value != 0:
                logical_scenario["bicycle"] = logical_scenario_template["bicycle"]
                logical_scenario["bicycle"]["LanePosition"]["s"][1] = float(road_len_dic["bicycle"]["LanePosition"]["max_length"])
                if json_output["scenario"] not in ["hero_and_bicycle_crossing_in_front"]:
                    del logical_scenario["bicycle"]["Events"]["BicycleStarts"]["ReachPositionCondition"]
                if logical_scenario["bicycle"]["Events"]["BicycleStarts"].get("ReachPositionCondition", 0) != 0:
                    logical_scenario["bicycle"]["Events"]["BicycleStarts"]["ReachPositionCondition"]["s"][1] = float(road_len_dic["bicycle"]["ReachPosition"]["max_length"])
                        
            elif "pedestrian" in actor and value != 0:
                for v in range(1, value+1):
                    if v == 1:
                        logical_scenario["pedestrian"] = logical_scenario_template["pedestrian"]
                        logical_scenario["pedestrian"]["LanePosition"]["s"][1] = float(road_len_dic["pedestrian"]["LanePosition"]["max_length"])
                        logical_scenario["pedestrian"]["Events"]["PedestrianStarts"]["ReachPositionCondition"]["s"][1] = float(road_len_dic["pedestrian"]["ReachPosition"]["max_length"])
                    else:
                        logical_scenario["pedestrian" + number_in_words[v-1]] = logical_scenario_template["pedestrian"]
                        logical_scenario["pedestrian" + number_in_words[v-1]]["LanePosition"]["s"][1] = float(road_len_dic["pedestrian" + number_in_words[v-1]]["LanePosition"]["max_length"])
                        logical_scenario["pedestrian" + number_in_words[v-1]]["Events"]["PedestrianStarts"]["ReachPositionCondition"]["s"][1] = float(road_len_dic["pedestrian" + number_in_words[v-1]]["ReachPosition"]["max_length"])
        
        weather_type = json_output["weather"]
        if "sun" in weather_type.lower():
            logical_scenario["weather"]["Sun"] = logical_scenario_template["weather"]["Sun"]

        elif "fog" in weather_type.lower():
            logical_scenario["weather"]["Fog"] = logical_scenario_template["weather"]["Fog"]

        elif "rain" in weather_type.lower():
            logical_scenario["weather"]["Precipitation"] = logical_scenario_template["weather"]["Precipitation"]

        logical_scenario["weather"]["RoadCondition"] = logical_scenario_template["weather"]["RoadCondition"]
        
        # the json file where the output must be stored 
        logical_scenario_path = store_path/"logical_scenario.json"
        out_file = open(logical_scenario_path, "w") 
        json.dump(logical_scenario, out_file, indent=4)

        return logical_scenario_path

    def func_to_logi_scenario_converter(self, user_text, store_path, llm_selector):
        
        ## functional to intermittent Json Converter. 
        json_output = self._func_to_json_converter(user_text, store_path, llm_selector)
        print(json_output)
        
        # comment me later - if json already exist. 
        # with open(store_path/"intermittent_json.json", "r") as j:
        #     json_output = json.load(j)

        # intermittent json to Logical Scenario Converter. 
        road_len_dic = self._choose_scenario_from_generated_scenario(json_output, store_path)
        # print(road_len_dic)

        logical_scenario_path = self._json_to_logi_converter(json_output, road_len_dic, store_path)

        # TODO - check for the length of road and replace it with the max

        return json_output, logical_scenario_path

    

        

