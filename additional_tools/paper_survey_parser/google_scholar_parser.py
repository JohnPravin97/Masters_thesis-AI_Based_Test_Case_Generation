import arxiv
# import streamlit
from dataclasses import dataclass
import datetime
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import pickle

"""
Steps for the publication detail finders. 

NOTE: Each component will be give with 5 different title combination. 

Google Scholar: 

Step 1: Give title and dates etc to the google scholar. 
Step 2: Choose few publication (see below for chosen ones) and select the papers only from there. 
Step 3: Retrieve the pub_details_container classes attributes from each of the publications. 

Chosen Publication are as follows: 
1. IEEE Xplore - ieeexplore.org - ICSE, ESEC/FSE
2. NeurIPS Proceedings - proceedings.neurips.cc
3. MDPI - mdpi.com
4. Proceedings of Machine Learning Research - proceedings.mlr.press
5. Association for computing machinery - dl.acm.org - ICSE, ESEC/FSE
6. arXiv - ICML, ICLR, AAAI, Neurips
7. openaccess.thecvf - CVPR, ICCV, ECCV

## ICML, ICLR, AAAI, Neurips - Artificial and ML top tier conferences. - Can be found in Arxiv 

If arxiv: 
    Use arxiv python api to get the info

For others: 
    Use a separate parsers. 
"""

# For advanced query syntax documentation, see the arXiv API User Manual:
# https://arxiv.org/help/api/user-manual#query_details

ALL_PUB_DETAILS_DIC = defaultdict(list)
ALL_GOOGLE_SCHOLAR_DETAILS_DIC = defaultdict(list)

WORDS = ["LLMs", "LLM", "generative", "pre-trained","Large Language Model", "Large Language Models", "GPT-4", "GPT", "GPT-3.5", "Flan-T5", "few-shot", "BERT", "ChatGPT", "Bard", "vicuna", "Language Model", "mistral", "LM"]

# NOTE [[a OR b] AND [] AND []]
ADDITIONAL_WORDS = {
    "scenario_generation_carla": [["scenario", "scene"], ["autonomous", "driving"], [ "generat"]], 
    "scenario_comprehension": [["scenario", "scene", "decision", "reasoning"], ["autonomous", "driving"], ["comprehen",  "interpret", "understand"]],
    "carla_code_generation": [["code"], ["generat"]], 
    "kpi_calculation": [["calculat"], ["maths", "math", "mathematical", "mathematics", "arithmetic"]],
    "requirement_tracability":[["requirement"], ["traceability", "tracing", "traceable", "trace"]],
    "requirement_generation":[["requirement"], ["generat"], ["autonomous", "driving", "driverless"]],
    "test_parameter_generation": [["test"], ["parameter"], ["generat"], ["autonomous", "driving", "driverless"]],
    "test_case_generation":[["test"], ["case"], ["generat"]]
    }

TOPIC = "requirement_tracability"
TITLE = "The use of LLMs in requirements traceability in software engineering"

@dataclass
class pub_details_container:
    entry_id: str
    title: str
    abstract: str
    updated: datetime.datetime
    authors: list
    pdf_url: str

@dataclass
class google_scholar_results_container:
    publication_name:str
    publication_authors: str
    publication_link: str

@dataclass
class title_count_details_container:
    total_results: int
    ieee_count: int
    neurips_count: int
    mdpi_count: int 
    mlr_count: int
    acm_count: int
    cvf_count: int 
    arxiv_count: int
    sciencedirect_count: int
    other_count: int


# #This can not be done
# def ieee_parser(link):
#     final_result = pub_details_container(...)
#     return final_result

def check(sentence, words, additional_words):
    # print(sentence)
    # print("\n\n")
    for word in words:
        if word.lower() in sentence.lower():
            #TODO - Done
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

def neurips_parser(link):
    relevant_count = 0

    # retrieve the data from arxiv
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "lxml")

    # Retrieve the details of the paper
    first_content = soup.find("div", class_="container-fluid")
    
    entry_id = None
    title = first_content.find_next("h4").text.strip()
    authors = first_content.find_next("h4").find_next("h4").find_next("p").text.strip()
    submitted = first_content.find_next("h4").find_next("p").text.strip()
    summary = first_content.text.split("Abstract")[-1].strip()
    
    if check(summary, WORDS, ADDITIONAL_WORDS[TOPIC]):
        relevant_count = 1

    return pub_details_container(entry_id, title, summary, submitted, authors, pdf_url=link), relevant_count

def mdpi_parser(link):
    relevant_count = 0

    # retrieve the data from arxiv
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "lxml")
    authors = []

    # Retrieve the details of the paper
    entry_id = None
    title = soup.find("h1", class_="title hypothesis_container").text.strip()
    summary = soup.find("div", class_="html-p").text.strip()
    submitted = soup.find("div", class_="pubhistory").text.strip()
    first_soup = soup.find("div", class_="art-authors hypothesis_container")

    for first_content in first_soup.find_all("span", class_="sciprofiles-link__name"):
        authors.append(first_content.text)
    
    authors = list(set(authors))

    if check(summary, WORDS, ADDITIONAL_WORDS[TOPIC]):
        relevant_count = 1

    return pub_details_container(entry_id, title, summary, submitted, authors, pdf_url=link), relevant_count

def mlr_parser(link):
    relevant_count = 0

    # retrieve the data from arxiv
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "lxml")

    # Retrieve the details of the paper
    entry_id = None
    title = soup.find("article", class_="post-content").find("h1").text.strip()
    authors = soup.find("span", class_="authors").text.strip()
    submitted = soup.find("div", id="info").text.strip()
    summary = soup.find("div", class_="abstract").text.strip()

    if check(summary, WORDS, ADDITIONAL_WORDS[TOPIC]):
        relevant_count = 1

    return pub_details_container(entry_id, title, summary, submitted, authors, pdf_url=link), relevant_count

def acm_parser(link):
    relevant_count = 0
    # retrieve the data from arxiv
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "lxml")
    authors = []
    
    # Retrieve the details of the paper
    entry_id = None
    title = soup.find("h1", class_="citation__title").text.strip()
    summary = soup.find("div", class_="abstractSection abstractInFull").text.strip()
    submitted = soup.find("span", class_="epub-section__date").text.strip()
    for first_content in soup.find_all("div", class_="author-data"):
        authors.append(first_content.text.strip())
    
    if check(summary, WORDS, ADDITIONAL_WORDS[TOPIC]):
        relevant_count = 1

    return pub_details_container(entry_id, title, summary, submitted, authors, pdf_url=link), relevant_count

def arxiv_parser(link):
    relevant_count = 0
    # retrieve the data from arxiv
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "lxml")

    # Retrieve the details of the paper
    entry_id = link.split("abs/")[-1]
    title = soup.title.text.strip()
    summary = soup.find("blockquote", class_="abstract mathjax").text.strip()
    submitted = soup.find("div", class_="dateline").text.strip()
    authors = soup.find("div", class_="authors").text.strip()

    if check(summary, WORDS, ADDITIONAL_WORDS[TOPIC]):
        relevant_count = 1

    return pub_details_container(entry_id, title, summary, submitted, authors, pdf_url=link), relevant_count

def cvf_parser(link):

    relevant_count = 0
    # retrieve the data from arxiv
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "lxml")

    # Retrieve the details of the paper
    entry_id = None
    title = soup.find("div", id="papertitle").text.strip()
    summary = soup.find("div", id="abstract").text.strip()
    submitted = soup.find("div", id="authors").text.strip().split(";")[1].strip()
    authors = soup.find("div", id="authors").text.strip().split(";")[0]

    if check(summary, WORDS, ADDITIONAL_WORDS[TOPIC]):
        relevant_count = 1

    return pub_details_container(entry_id, title, summary, submitted, authors, pdf_url=link), relevant_count

def dict_from_class(cls):
    return dict((key, value) for (key, value) in cls.__dict__.items())

def main():
    # Google Scraper      
    title = TITLE
    page = 0
    url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={title}&oq="
    ieee_count, neurips_count, mdpi_count, mlr_count, acm_count, cvf_count, arxiv_count, sciencedirect_count, other_count = 0, 0, 0, 0, 0, 0, 0, 0, 0 
    relevant_pub_count = 0
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    no_of_results = soup.find("div", id="gs_ab_md").text.split("results")[0].split("About")[-1].strip()
    print(TITLE)
    print("Total_no_of_results", no_of_results)
    total_results = int(no_of_results.replace(".", ""))
    # num_pages = int(total_results/10)
    num_pages = 100
    print("total_pub_scraped", num_pages)

    while page < num_pages:
        url = f"https://scholar.google.com/scholar?start={page*10}&q={title}&hl=en&as_sdt=0,5"

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        google_scholar_results = soup.find_all("div", class_="gs_ri")

        for google_scholar_result in google_scholar_results:
            result = None
            publication_name = google_scholar_result.find("h3", class_="gs_rt").text
            publication_authors = google_scholar_result.find("div", class_="gs_a").text
            # publication_name = 
            publication_link = google_scholar_result.find("a")["href"]
            google_scholar_results = google_scholar_results_container(publication_name, publication_authors, publication_link)

            # run a loop on all the relevant search results and pass it to individual functions for further
            if "ieeexplore.ieee.org" in publication_authors:
                # Since IEEE is not allowed to scraper
                try:
                    ieee_count += 1
                except: 
                    pass
                # TODO make a arxiv parser for this.
            

            
            elif "proceedings.neurips.cc" in publication_authors:
                try: 
                    result, relevant_count = neurips_parser(publication_link)
                    neurips_count += 1
                    relevant_pub_count+=relevant_count
                except: 
                    pass
            
            elif "mdpi" in publication_authors:
                try: 
                    result, relevant_count = mdpi_parser(publication_link)
                    mdpi_count += 1
                    relevant_pub_count+=relevant_count
                except: 
                    pass
            
            elif "proceedings.mlr" in publication_authors:
                try:
                    result, relevant_count = mlr_parser(publication_link)
                    mlr_count += 1
                    relevant_pub_count+=relevant_count
                except: 
                    pass
            
            elif "dl.acm" in publication_authors:
                try:
                    result, relevant_count = acm_parser(publication_link)
                    acm_count+=1
                    relevant_pub_count+=relevant_count
                except: 
                    pass
            
            elif "openaccess.thecvf.com" in publication_authors:
                try:
                    result, relevant_count = cvf_parser(publication_link)
                    cvf_count+=1
                    relevant_pub_count+=relevant_count
                except: 
                    pass
            
            elif "arxiv.org" in publication_authors:
                try:
                    result, relevant_count = arxiv_parser(publication_link)
                    arxiv_count+=1
                    relevant_pub_count+=relevant_count
                except: 
                    pass
            elif "Elsevier" in publication_authors:
                sciencedirect_count+=1
        
            else:
                other_count+=1
            
            ALL_PUB_DETAILS_DIC[title].append(result)
            ALL_GOOGLE_SCHOLAR_DETAILS_DIC[title].append(google_scholar_results)
            page+=1
            # print(f"Done scraping page number {page}")

    title_count = title_count_details_container(total_results= num_pages, ieee_count=ieee_count, neurips_count= neurips_count, mdpi_count = mdpi_count, mlr_count = mlr_count, acm_count= acm_count, cvf_count = cvf_count, arxiv_count= arxiv_count, sciencedirect_count= sciencedirect_count, other_count=other_count)

    print(title_count)
    print("relevant_count", relevant_pub_count)

    # print(ALL_PUB_DETAILS_DIC[title])
    with open(f"{title}_pub.pkl", "wb") as f:
        pickle.dump(ALL_PUB_DETAILS_DIC[title], f)
    
    with open(f"{title}_google_scholar_pub.pkl", "wb") as f:
        pickle.dump(ALL_GOOGLE_SCHOLAR_DETAILS_DIC[title], f)

    with open(f"{title}_counts.pkl", "wb") as f:
        pickle.dump(title_count, f)

if __name__ == "__main__":
    main()
