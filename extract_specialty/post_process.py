import glob
import csv

from app import read_csv

# read in all processed_ files
#f = glob.glob('processed_*.csv')

#tt[tt.find('PROCEDURE : ')+len('PROCEDURE : '):len(tt)] # from procedure to end

# find to next \n
def find_features(response_text):
    pt = 'PROCEDURE : '
    an  = 'ANATOMICAL: '
    sp = 'SPECIALTY'
    # procedure is between procedure and anatomical
    proc_loc = response_text.find(pt)+len(pt)
    following = response_text[proc_loc:].find('\n')
    procedure = response_text[proc_loc:proc_loc+following].strip(':')
    # anatomical is between anatomical and specialty
    ana_loc = response_text.find(an)+len(an)
    following = response_text[ana_loc:].find('\n')
    anatomical = response_text[ana_loc : ana_loc+following].strip(':')

    # specialty is between specialty and <eot_id>
    sp_loc = response_text.find(sp)+len(sp)
    following=response_text[sp_loc:].find('<|eot_id|>')
    specialty = response_text[sp_loc:sp_loc+following].strip(':')
    return {'procedure':procedure, 'anatomical':anatomical, 'specialty':specialty}

# For each row fo each file this will return a value.

#ff = [post_process.find_features(a['response']) for a in aa]
#[a.update(post_process.find_features(a['response']) for a in aa] # will update each element of the list of dicts to include procedure, anatomy, specialty.
def sortfun(e):
    # remove extraneous
    ee = e[e.rfind('_')+1:].strip('.csv')
    return int(ee) 

def process_files():
    gg = glob.glob('processed*.csv')
    gg.sort(key=sortfun)# WORKS
    hh = []
    for file in gg:
        ff=read_csv(file)
        # update with post_process
        [f.update(find_features(f['response'])) for f in ff]
        hh = hh + ff
    with open('pmid_response.csv','w', newline ='') as of:
        dict_writer = csv.DictWriter(of, ['PMID', 'Abstract', 'response', 'procedure', 'anatomical','specialty'])
        dict_writer.writeheader()
        dict_writer.writerows(hh)
    return hh
    # save
