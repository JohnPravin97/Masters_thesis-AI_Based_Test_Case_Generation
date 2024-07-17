import arxiv
# import streamlit
from dataclasses import dataclass
import datetime
from collections import defaultdict
import pickle
import numpy as np

ALL_PUB_DETAILS_DIC = defaultdict(list)
WORDS = ["pre-trained","Large Language Model", "GPT-4", "GPT-3.5", "Flan-T5", "BERT", "few-shot", "ChatGPT", "vicuna",  "mistral", "Claude"]

# Part of the thesis
# NOTE [[a OR b] AND [] AND []]
ADDITIONAL_WORDS = {
    "scenario_generation_carla": [["scenario", "scene"], ["autonomous", "driving"], [ "generat"]], 
    "scenario_comprehension": [["scenario", "scene", "decision", "reasoning"], ["autonomous", "driving"], ["comprehen",  "interpret", "understand"]],
    "carla_code_generation": [["code"], ["generat"]], 
    "kpi_calculation": [["calculat"], ["maths", "math", "mathematical", "mathematics", "arithmetic"]],
    "requirement_tracability":[["requirement"], ["traceability", "tracing", "traceable", "trace"]],
    "requirement_generation":[["requirement"], ["generat"], ["autonomous", "driving", "driverless"]],
    "test_parameter_generation": [["test"], ["parameter"], ["generat"], ["autonomous", "driving", "driverless"]],
    "test_case_generation":[["test"], ["case"], ["generat"], ["autonomous", "driving", "driverless"]]
    }

# # Overall Software Engineering Survey
# ADDITIONAL_WORDS = {
#     "Requirement_engineering_1": [["Requirement", "Anaphoric"], ["extraction", "traceability", "validation", "classification", "retrieval", "completeness"]],
#     "Requirement_engineering_2": [["Anaphoric"], ["ambiguity"]],
#     "System_design_1":[["GUI"], ["retrieval"]],
#     "System_design_2":[["Rapid"], ["prototyp"]],
#     "Software_development":[["code"], ["represent", "generat", "search", "translat", "complet", "edit", "summariz"]],
#     "Software_quality_assurance_1": [["bug"], ["localization", "detect", "classificat"]],
#     "Software_quality_assurance_2": [["fault"], ["localization"]],
#     "Software_quality_assurance_3": [["test"], ["case"], ["automat", "generate", "predict"]],
#     "Software_quality_assurance_4": [["static"], ["analysis"]],
#     "Software_maintenance_1": [["program"], ["repair"]],
#     "Software_maintenance_2": [["code"], ["review", "classificat", "debugg"]],
#     "Software_maintenance_3": [["bug"], [ "report", "reproduct"]],
#     "Software_management": [["effort"], ["estimat", "predict"]]
# }


# https://arxiv.org/category_taxonomy

# CATEGORIES = ["cs.AI", "cs.CL", "cs.CV", "cs.SE", "cs.PL"]
# QUERY = 'cat: cs.AI OR cat: cs.SE OR cat: cs.PL'

QUERY = "cat: cs.SE OR cat: cs.PL" # choose from cat: cs.SE,  cat: cs.PL, cat: cs.CL

def check(sentence, words, additional_words):
    # print(sentence)
    # print("\n\n")
    for word in words:
        if word.lower() in sentence.lower():
            #TODO
            found_me_lis = []
            for additional_word in additional_words:
                found_me = False
                for add_word in additional_word:
                    if add_word.lower() in sentence.lower():
                        found_me = True
                found_me_lis.append(found_me)
            if all(found_me_lis):                
                return True
    return False

def check_only_LLMs(sentence, words):
    # print(sentence)
    # print("\n\n")
    for word in words:
        if word.lower() in sentence.lower():
            return True
    return False

def arxiv_parser(query, max_value = 1000000):
    final_result = []
    # Construct the default API client.
    client = arxiv.Client()
    # Search for the paper with ID 
    search = arxiv.Search(query = query, sort_by = arxiv.SortCriterion.SubmittedDate, max_results = max_value) # max_results = 10
    for r in client.results(search):
        pub_details_container = {}
        pub_details_container["entry_id"] = r.entry_id
        pub_details_container["title"] = r.title
        pub_details_container["abstract"] = r.summary
        pub_details_container["updated"] = r.updated
        pub_details_container["authors"] = r.authors
        pub_details_container["doi"] = r.doi
        pub_details_container["categories"] = r.categories
        pub_details_container["pdf_url"] = r.pdf_url
        final_result.append(pub_details_container)
        total_results = len(final_result)
        filename = f"paper_survey_parser/query_SE_PL_AI_arxiv_pub_total_{total_results}.pkl"
        if total_results % 1000 == 0: 
            with open(filename, "wb") as f:
                pickle.dump(final_result, f)

             
    with open(filename, "wb") as f:
        print("Final One")
        print(len(final_result))
        pickle.dump(final_result, f)

def read_parser(filename, topic="", only_llms = False):
    relevant_results = 0
    dates_list = []

    with open(filename, "rb") as f:
        publications = pickle.load(f)
    
    for publication in publications:
        if only_llms:
            title_check = check_only_LLMs(sentence=publication["title"], words=WORDS)
            abstract_check = check_only_LLMs(sentence=publication["abstract"], words=WORDS)
            if title_check or abstract_check:
                relevant_results+=1

                print(publication["title"])
                dates_list.append(publication['updated'].year)
        else:
            title_check = check(sentence=publication["title"], words=WORDS, additional_words = ADDITIONAL_WORDS[topic])
            abstract_check = check(sentence=publication["abstract"], words=WORDS, additional_words = ADDITIONAL_WORDS[topic])
            if title_check or abstract_check:
                # print(publication["abstract"])
                relevant_results+=1
                # if publication['updated'].year not in [2023, 2024]:
                #     print(publication["title"])
                print(publication["title"])
                dates_list.append(publication['updated'].year)
    
    values, counts = np.unique(np.array(dates_list), return_counts=True)

    print(values, counts)

    return {"topic": topic, "relevant_results": relevant_results}

def read_category_according_to_date(filename):
    dates_list = []
    with open(filename, "rb") as f:
        publications = pickle.load(f)

    for publication in publications:
        dates_list.append(publication['updated'].year)

    values, counts = np.unique(np.array(dates_list), return_counts=True)

    print(values, counts)

def main():
    # # Only for ARXIV
    
    # scrape as per the category details.
    # arxiv_parser(query= QUERY)

    # NOTE no category division
    
    # filename = f"paper_survey_parser/query_PL_arxiv_pub_total_7593.pkl"
    filename = f"additional_tools\paper_survey_parser\query_SE_PL_arxiv_pub_total_22238.pkl"
    # read_category_according_to_date(filename)

    # topic_dic = read_parser(filename, only_llms=True)
    # print("only LLMs: True")
    # print("relevant_results", topic_dic["relevant_results"])

    # topics = ["scenario_generation_carla", "scenario_comprehension", "carla_code_generation", "kpi_calculation", "requirement_tracability", "requirement_generation", "test_parameter_generation", "test_case_generation"]
    topics = list(ADDITIONAL_WORDS.keys())
    print(topics)
    for idx, topic in enumerate(topics):
        if idx ==12:
            topic_dic = read_parser(filename, topic, only_llms=False)
            # print("only LLMs: False")
            print("topic", topic)
            print("relevant_results", topic_dic["relevant_results"])
            print("--------------------")
        

if __name__ == "__main__":
    main()

