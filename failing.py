import os, sys
import re
import pickle
import pandas as pd

################################################################################
############################# FUNCTION #########################################
################################################################################

def errorloc(e):
    print(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)

def recoverData(path_data, pattern):
    pattern_data_failed = pattern
    patternc_data_failed = re.compile(pattern_data_failed)
    names_data_failed = []

    for filename in os.listdir(f'{path_data}'):
        # print(filename)
        if patternc_data_failed.match(filename):
            # print(filename)
            name, form = filename.split('.')
            names_data_failed.append(name)
        else:
            continue

    names_data_failed.sort(key=natural_keys)

    return names_data_failed

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


def recoverPickleRick(path_data, name_file):
    backup_file = open(f"{path_data}/{name_file}.pkl", "rb")
    recoveredPickle = pickle.load(backup_file)
    backup_file.close()
    return recoveredPickle

def savePickleRick(path_data, name_file, data):
    backup_file = open(f"{path_data}/{name_file}.pkl", "wb")
    pickle.dump(data, backup_file)
    backup_file.close()

def recoveredToTempWriter(names, path_data, data, temp_data_writer):
    if len(names) > 0:
        print('\nRecovering data from temporal failed attempt\n')
        recovered_data = pd.read_csv(f"{path_data}/{names[-1]}.csv")
        lsrd = recovered_data.to_dict('list')
        data = {key: lsrd[key] for key, value in lsrd.items()}
        print(data)

        for di, ds in enumerate(data['subject']):
            pastTemprow = []
            # print(ds)
            keys = data.keys()
            for k in keys:
                pastTemprow.append(data[k][di])

            temp_data_writer.writerow(pastTemprow)