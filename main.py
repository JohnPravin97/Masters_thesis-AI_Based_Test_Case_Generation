from adapt_and_manipulate_scenario.functional_to_logical_scenario import Func2LogiConvertor
from adapt_and_manipulate_scenario.logical_to_concrete_scenario import logi_to_concrete_scenario_converter
from adapt_and_manipulate_scenario.utils.scenario_manipulator import ScenarioManipulate
from pathlib import Path
import os
import json
import subprocess
import time 

PARENT = Path.cwd().parent 
llm_selector = "OpenAI" # ["OpenAI", "WizardLM", "MistralAI"]
sampling_methods = "bayesian_optimization" # ["random", "bayesian_optimization", "LLM"]

def main():

    # STEP 1 - Initialization
    out_path = "out/test_01"
    input_folder = PARENT / Path(out_path).resolve()
    
    # STEP 2 - Test parameter space generation
    with open(next(input_folder.glob("*.txt")), "r") as f:
        text = f.read()
    
    ## Test parameter generation - Comment me if already test parameters are generated
    intermittent_json_output, logical_scenario_path = Func2LogiConvertor().func_to_logi_scenario_converter(text, input_folder, llm_selector=llm_selector)

    in_scenario_file = str(next(input_folder.glob("*.xosc")))
    
    # comment me when you need to generate Test parameter
    # logical_scenario_path = input_folder/"logical_scenario.json"
    # with open(input_folder/"intermittent_json.json", "r") as j:
    #     intermittent_json_output = json.load(j)

    for epoch in range(1, intermittent_json_output["iterations"]+1):
        
        # STEP 3 - Test case generation
        folder_name = sampling_methods + "/iteration_" + str(epoch)
        iteration_folder = input_folder / Path(folder_name)
        iteration_folder.mkdir(parents=True, exist_ok=True)
        
        concrete_scenario, vehicle_types = logi_to_concrete_scenario_converter(input_folder, epoch, intermittent_json_output, logical_scenario_path, iteration_folder, sampling_methods)
        
        # STEP 4 - Scenario Manipulation
        sm = ScenarioManipulate(parameter_json=concrete_scenario,  map_name = intermittent_json_output["map"], vehicle_types=vehicle_types, scenario_location=intermittent_json_output["road"], scenario_information=intermittent_json_output["scenario"])
        
        out_scenario_file = str(iteration_folder / "editted.xosc")
        sm.scenario_manipulate(in_scenario_file=in_scenario_file, out_scenario_file=out_scenario_file)


        # # STEP 5 - Simulation
        eval_outputpath = PARENT / Path(f"evaluation/logi_2_concrete/{sampling_methods}/{out_path.split('/')[-1]}_results.txt").resolve()
        cmd = ['/bin/python3', 'scenario_runner/scenario_runner.py', '--openscenario', out_scenario_file, "--outputDir", str(iteration_folder), "--output", "--file", ]
        manual_py_cmd = ['/bin/python3', 'scenario_runner/manual_control.py', "--output_filepath", str(iteration_folder)] 
        
        try:    
            # Call Lanchangedev.py with the speed argument
            result = subprocess.Popen(cmd)
        
            # Call Lanchangedev.py with the speed argument
            result2 = subprocess.Popen(manual_py_cmd)

            # Check if the command completed successfully
            result.wait()
            result2.wait()

            if result.returncode== 0:
                print('scenario runner script completed successfully.')
            else:
                print('scenario runner script failed with return code:', result.returncode)
                print('Error scenario runner message:', result.stderr)
                
        except subprocess.CalledProcessError as e:
            # Log any errors that occur during the subprocess call
            print(f"Command failed with return code {e.returncode}")
            print("Error message:", e.stderr)

        try: 
            with open(next(iteration_folder.glob("*.txt")), "r") as f:
                text = f.readlines()
                if "SUCCESS" in text[1]:
                    result = "SUCCESS"
                else:
                    result = "FAILED"
                time_taken = text[17].strip().split("│ Game Time             │ ")[1].split("s")[0]
        
        except: 
            raise Exception("The output file is not generated")

        # end_time = time.time()
        # Save the evaluation results of the adapted scenarios
        with open(eval_outputpath, "a+") as eval_file:
            output_iteration = f"Test_Number= {out_path.split('_')[-1]},\n Iterations = {epoch}, Technique_Used = '{sampling_methods}', \n Scenario_name = '{intermittent_json_output['scenario']}', Time_Taken = {time_taken}s, Result = {result} \n\n"
            eval_file.write(output_iteration)

        assert iteration_folder.exists(), "iteration folder does not exist"
              
if __name__ == "__main__":
    main()

    