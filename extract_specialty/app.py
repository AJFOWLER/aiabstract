import os
import csv
import re
import requests
from Bio import Entrez

def read_csv(file):
    holder =  []
    with open(file, 'r', errors='ignore') as f:
        for r in csv.DictReader(f):
            holder.append(r)
    return holder

def process_pmid(file):
    f = read_csv(file)
    #try with 5 for now!
    pmids = ','.join([x['pmid_master'] for x in f])
    # now grab abstracts
    Entrez.email = 'alexjfowler@gmail.com'
    handle = Entrez.efetch(db='pubmed', id=pmids, rettype='xml', retmode='text')
    records = Entrez.read(handle)
    handle.close()
    all_abstracts = []## holder
    for article in records["PubmedArticle"]:
        a = article["MedlineCitation"]["Article"]
        pmid = article["MedlineCitation"]["PMID"]
        if "Abstract" in a:
            abs_t = a["Abstract"]["AbstractText"]
            if isinstance(abs_t, list):
                abstract = " ".join(str(section) for section in abs_t)
            else:
                abstract = str(abs_t)
            all_abstracts.append((str(pmid), abstract))
        else:
            all_abstracts.append((str(pmid), 'NONE'))
    return all_abstracts 

def save_abs(file):
    all_abstracts = process_pmid(file)

    with open('pmid_abstracts.csv', 'w', newline="", encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['PMID', 'Abstract'])
        writer.writerows(all_abstracts)
        print('written to pmid_abstracts.csv')

def parse_llm(prompt):
    api_endpoint ="http://localhost:8080/v1/chat/completions" 
    payload = {
        "messages": [{"role":"user",
                      "content": prompt}],
        "n_predict" : 2048,
        "temperature":0.16,
        "stream": False
    }
    try: 
        response = requests.post(api_endpoint, json=payload, timeout=1000)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Error querying: {e}")
        return None

def classify(file):
    pmid_file = read_csv(file)
    prompt_template_2 = """
    You are a bot classifying medical literature. Please identify the medical or surgical procedure that is studied or described in the abstract below. If possible, extract the procedure directly. Format to return:
        PROCEDURE : insert name of procedure
        ANATOMICAL: insert name of body part operated on
        SPECIALTY: insert medical specialty most likely to perform the procedure or treat the problem described.
    The abstract is below:
    """
    prompt_template = """
    You are a bot classifying medical literature abstracts according to the type of surgery they describe or the specialty involved. For example, if describing uterine embolisation, this would be gynaecological surgery. If it involved coronary surgery, it would be classed as cardiac surgery. Surgery on blood vessels would be vascular surgery
    Please return what you think is the most appropriate specialty in as few words as possible.
    The abstract you are to classify is here:
    """

    output = []
    # do in chunks of 10 abstracts.
    i = 1
    for x in pmid_file[1001:1500]:
        print(i)
        i+=1
        prompt = prompt_template_2 + x['Abstract']
        result = parse_llm(prompt)
        x['response'] = result
        output.append(x)
    return output

#17/8 - 0:704
# 704 onwards.
def save_parsed(f, n):
    with open(n, 'w', newline='') as of:
        dict_writer = csv.DictWriter(of, ['PMID', 'Abstract', 'response'])
        dict_writer.writeheader()
        dict_writer.writerows(f)
