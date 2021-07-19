from classes_conds import ConditionsHandler
from classes_testData import TestingDataHandler
from failing import *
from saving_data import *


import argparse

def mkpaths(situ, numdaysubj = None, folder_name = None):
    if situ == 'tb':
        path_day, path_data, path_figs, path_datalocal = folderChreation(numdaysubj, 'n', folder_name)
        path_videos = folderVhrideos(numdaysubj, 'n', folder_name)
        path_audio = folderArudio(numdaysubj, 'n', folder_name)
    elif situ == 'ex':
        path_day, path_data, path_figs, path_datalocal = folderChreation(numdaysubj, 'y', folder_name)
        path_videos = folderVhrideos(numdaysubj, 'y', folder_name)
        path_audio = folderArudio(numdaysubj, 'y', folder_name)

    return path_day, path_data, path_figs, path_datalocal, path_videos, path_audio

def parsing_situation():
    parser = argparse.ArgumentParser(description='Experimental situation: troubleshooting (tb) or experimenting (ex)')
    parser.add_argument('-s', type=str)
    parser.add_argument('-p', type=str, default=None)
    args = parser.parse_args()
    situ = args.s
    part = args.p

    return situ, part

def experiment_part():
    parser = argparse.ArgumentParser(description='Experiment part: folder name')
    

    args = parser.parse_args()
    part = args.p

    return part