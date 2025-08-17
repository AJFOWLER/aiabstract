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
# So now we have used an embedding type set up. This involves embedding all the titles & abstracts, then simply using the embedding to search for them.
# No actual RAG as yet, but let's see how many of the human selected are in the top 650?

embed_data = pd.read_json('embedding_results.json')
#titles
embed_select = [x[1][0] for x in embed_data.iterrows()]

len(set(embed_select[0:10]) & set(human_select)) #3 of select papers in top 10
len(set(embed_select[0:20]) & set(human_select)) #5 of select papers in top 20
len(set(embed_select[0:40]) & set(human_select)) #11 of select papers in top 10
len(set(embed_select[0:100]) & set(human_select)) #13 of select papers in top 10
len(set(embed_select[0:713]) & set(human_select)) #20 of select papers in top 650
# On it's own this isn't terrible; we only selected the top ~750 papers after embedding them (got stuck at 713)
# Actually this looks pretty impressive as a simple step to be done on it's own

next(ips.iterrows())
#estimate first 650 assuming rayyan keys in order of review?
rayyan_keys = [int(k[1]['key'].strip('rayyan-')) for k in ips.iterrows()]
rk = [x - rayyan_keys[0] for x in rayyan_keys]
len([i for i in rk if i <713]) #~20 selected papers in these 650.
# What is the distribution of these?
# If we compare vs. how many articles you had to look at to get the top twenty in rk==> This is much better!
# top 10 in RK requires looking at 218, vs. 40 here! I'm sure you could do something to improve this.
