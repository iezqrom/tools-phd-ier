import numpy as np
import random
from math import gcd
from text import *


class ConditionsHandler:
    def __init__(self, *conds):
        self.conditions = np.array(np.meshgrid(*conds)).T.reshape(-1, len(conds))

    def repeatition(self, n_repeats):
        self.random_repeats = np.repeat(self.conditions, n_repeats, axis=0)
        np.random.shuffle(self.random_repeats)


#################################################################
########################## FUNCTIONS ############################
#################################################################


def sdtSetup(n_trials, conds, randomised=True):
    """
    Function to set-up trials for a Signal Detection Theory experiment.
    The number of trials will be distributed equally across the number of conditions.
    For instance, if we have 1 condition (e.g. cold stimulation with touch),
    and you set n_trials = 10, there'll be 10 trials of this condition.
    However, if we have 2 conditions (e.g. cold stimulation with and without touch),
    and you set n_trials = 10, there'll be 5 trials of each condition.
    Stimulus absent and present are coded with 0s (absent) and 1s (present), respectively.
    Conditions are coded from 0-n.
    Condition and stimulus absent/present come in tuples.

    position 0: condition
    position 1: catch trial
    position 2: touch
    position 3: reverse
    position 4: fake
    """

    stimulations = []

    if not n_trials % (2 * conds) == 0:
        printme(f"Number of trials is not divisable by {2*conds}")
        if not n_trials % 2 == 0:
            printme(f"Number of trials is an odd number")
        printme("WARNING: Uneven number of conditions")
        code_conds = np.arange(conds)
        n_cond_trials = n_trials / conds

        n_conds = np.repeat(code_conds, n_cond_trials, axis=0)
        unique, counts = np.unique(n_conds, return_counts=True)
        print(counts)

        for u, c in zip(unique, counts):
            abs_pres = np.repeat([0, 1], c, axis=0)

            for ap in abs_pres:
                stimulations.append((u, ap))
        if randomised:
            np.random.shuffle(stimulations)
        stimulations = stimulations[:n_trials]

    else:
        code_conds = np.arange(conds)
        n_cond_trials = n_trials / conds

        n_conds = np.repeat(code_conds, n_cond_trials, axis=0)
        unique, counts = np.unique(n_conds, return_counts=True)
        # print(counts)

        for u, c in zip(unique, counts):
            abs_pres = np.repeat([0, 1], c / 2, axis=0)

            for ap in abs_pres:
                stimulations.append((u, ap))
        if randomised:
            np.random.shuffle(stimulations)

    return stimulations


def factorization(n):
    """
    Function to perform integer factorization
    """

    factors = []

    def get_factor(n):
        x_fixed = 2
        cycle_size = 2
        x = 2
        factor = 1

        while factor == 1:
            for count in range(cycle_size):
                if factor > 1:
                    break
                x = (x * x + 1) % n
                factor = gcd(x - x_fixed, n)

            cycle_size *= 2
            x_fixed = x

        return factor

    while n > 1:
        next = get_factor(n)
        factors.append(next)
        n //= next

    return factors
