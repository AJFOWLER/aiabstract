#import rispy
from risclassifier import RISClassifier
#import time
#with open('file.ris', 'r', encoding='utf-8') as file:
#    entries = rispy.load(file)

#for entry in entries:
 #   print(entry)
  #  print('---')

#missing_abstract = [x for x in entries if 'abstract' not in x]
# 321 have no abstract.
#These are mostly genuine!
classifier = RISClassifier()
entries = classifier.load_ris_file('post_duplicate_removal_22May2025.ris')
your_criteria = "select only studies including humans undergoing surgery and the effect of e-cigarettes or vaping or electronic cigarette use on outcomes after surgery."
#start = time.time()
results = classifier.classify_entries(entries, your_criteria)
#stop = time.time()
#difference = stop-start

#TODO:
#1. Add 'missing abstract' or similar to prompt
#2. Make baseline pattern to be 'missing response' rather than exclude.

# should save to a .json file
# Filter results
#included_papers = [r for r in results if r['decision'] == 'INCLUDE']
#high_confidence = [r for r in results if r['confidence'] == 'High'] 
#Llama works poorly
#Deepseek-R1-Distill-Qwen-1.5B is slow and everything is in 'thinking' mode so it's output is very hard to capture....
# To use deepseek have to sack off 'stop' sequence.

