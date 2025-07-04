import os
import pandas as pd
cwd = os.getcwd()
# included papers
ippath = 'C:\\Users\\Buzzl\\Dropbox\\PostDoc\\Vaping\\SRMA\searchs\\included_papers.csv' 
ips = pd.read_csv(ippath)

# selected papers by the machine
sps = pd.read_json('results.json')

## overlap of selected papers
sps_ = [x for x in sps.iterrows() if x[1]['decision'] == "INCLUDE"]
len(sps_) # computer chooses 212!

## need to hunt by title
machine_select = [x[1]['title'] for x in sps_]

human_select = [x[1]['title'] for x in ips.iterrows()]

len(set(machine_select) & set(human_select)) # 11 - not very good

# try RAG
