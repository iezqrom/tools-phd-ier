import pandas as pd
from scipy.stats import norm
import math
import numpy as np

Z = norm.ppf


def tableTosdtDoble(table, num_sdt, name_response = "responses", name_stimulus = "cold", name_interactor = "touch"):
    table_single_sdt = table.loc[table[name_interactor] == num_sdt]

    table_cold = table_single_sdt.loc[table_single_sdt[name_stimulus] == 1]
    table_nocold = table_single_sdt.loc[table_single_sdt[name_stimulus] == 0]

    present_yes = table_cold.loc[table_cold[name_response] == 1]
    present_no = table_cold.loc[table_cold[name_response] == 0]

    absent_yes = table_nocold.loc[table_nocold[name_response] == 1]
    absent_no = table_nocold.loc[table_nocold[name_response] == 0]

    return present_yes, present_no, absent_yes, absent_no


def correctPercSDT(subtables, name_response = "responses"):
    out = {}

    present_yes = subtables[0]
    present_no = subtables[1]
    absent_yes = subtables[2]
    absent_no = subtables[3]

    out["hits"] = len(present_yes.loc[:, name_response])
    out["misses"] = len(present_no.loc[:, name_response])

    out["fas"] = len(absent_yes.loc[:, name_response])
    out["crs"] = len(absent_no.loc[:, name_response])

    out["correc_present"] = round(out["hits"] / sum([out["hits"], out["misses"]]), 3)
    out["correc_absent"] = round(out["crs"] / sum([out["crs"], out["fas"]]), 3)

    return out


def SDTextremes(hits, misses, fas, crs):
    """returns a dict with d-prime measures given hits, misses, false alarms, and correct rejections"""
    # Floors an ceilings are replaced by half hits and half FA's
    half_hit = 0.5 / (hits + misses)
    half_fa = 0.5 / (fas + crs)

    # Calculate hit_rate and avoid d' infinity
    hit_rate = hits / (hits + misses)
    if hit_rate == 1:
        hit_rate = 1 - half_hit
    if hit_rate == 0:
        hit_rate = half_hit

    # Calculate false alarm rate and avoid d' infinity
    fa_rate = fas / (fas + crs)
    # print(fa_rate)
    if fa_rate == 1:
        fa_rate = 1 - half_fa
    if fa_rate == 0:
        fa_rate = half_fa

    # print(hit_rate)
    # print(fa_rate)

    # Return d', beta, c and Ad'
    out = {}
    out["d"] = Z(hit_rate) - Z(
        fa_rate
    )  # Hint: normalise the centre of each curvey and subtract them (find the distance between the normalised centre
    out["beta"] = math.exp((Z(fa_rate) ** 2 - Z(hit_rate) ** 2) / 2)
    out["c"] = (
        Z(hit_rate) + Z(fa_rate)
    ) / 2  # Hint: like d prime but you add the centres instead, find the negative value and half it
    out["Ad"] = norm.cdf(out["d"] / math.sqrt(2))
    out["hit_rate"] = hit_rate
    out["fa_rate"] = fa_rate
    out["correct"] = (out["hits"] + out["crs"]) / (
        out["hits"] + out["misses"] + out["fas"] + out["crs"]
    )

    return out


def SDTloglinear(hits, misses, fas, crs):
    """returns a dict with d-prime measures given hits, misses, false alarms, and correct rejections"""
    # Calculate hit_rate and avoid d' infinity
    hits += 0.5
    hit_rate = hits / (hits + misses + 1)

    # Calculate false alarm rate and avoid d' infinity
    fas += 0.5
    fa_rate = fas / (fas + crs + 1)

    # print(hit_rate)
    # print(fa_rate)

    # Return d', beta, c and Ad'
    out = {}
    out["d"] = Z(hit_rate) - Z(
        fa_rate
    )  # Hint: normalise the centre of each curvey and subtract them (find the distance between the normalised centre
    out["beta"] = math.exp((Z(fa_rate) ** 2 - Z(hit_rate) ** 2) / 2)
    out["c"] = (
        Z(hit_rate) + Z(fa_rate)
    ) / 2  # Hint: like d prime but you add the centres instead, find the negative value and half it
    out["Ad"] = norm.cdf(out["d"] / math.sqrt(2))
    out["hit_rate"] = hit_rate
    out["fa_rate"] = fa_rate
    out["correct"] = (hits + crs) / (hits + misses + fas + crs)

    out['percent_hits'] = hits / (hits + misses)*100
    out['percent_crs'] = crs / (fas + crs)*100

    return out


def SDTAprime(hits, misses, fas, crs):
    """
    Original equation: Pollack & Norman, 1979
    Adapted: Stanislaw and Todorov
    """
    # Calculate hit_rate and avoid d' infinity
    hit_rate = hits / (hits + misses)

    # Calculate false alarm rate and avoid d' infinity
    fa_rate = fas / (fas + crs)

    # print(hit_rate)
    # print(fa_rate)

    # Return d', beta, c and Ad'
    out = {}
    # out['Aprime'] = 1 - (1/4) * ( (fa_rate/hit_rate) + ((1-hit_rate)/(1-fa_rate))) # pollack & norman
    out["Aprime"] = 0.5 + (
        np.sign(hit_rate - fa_rate)
        * (
            ((hit_rate - fa_rate) ** 2 + abs(hit_rate - fa_rate))
            / (4 * max(hit_rate, fa_rate) - 4 * hit_rate * fa_rate)
        )
    )  # adapted
    out["hit_rate"] = hit_rate
    out["fa_rate"] = fa_rate

    return out
