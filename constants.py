#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
cosi217b - AMR2KB
alexluu@brandeis.edu
Python 3.4
"""
import os

PROJECT = os.getcwd()
TEXT = os.path.join(PROJECT, '1_text')
AMR = os.path.join(PROJECT, '2_amr')
KB = os.path.join(PROJECT, '3_kb')
AMR_PILOT = os.path.join(AMR, 'pilot')
AMR_PILOT_TRAIN = os.path.join(AMR_PILOT, 'train')
AMR_PILOT_DEV = os.path.join(AMR_PILOT, 'dev')
AMR_PILOT_TEST = os.path.join(AMR_PILOT, 'test')
#...
AMR_PILOT_SELECTED = os.path.join(AMR_PILOT, 'selected')
AMR_PILOT_SELECTED_ALIGNED = os.path.join(AMR_PILOT, 'selected_aligned')
AMR_PILOT_SELECTED_PKL = os.path.join(AMR_PILOT, 'selected_pkl')
#AMR_PILOT_SELECTED_JSN = os.path.join(AMR_PILOT, 'selected_jsn')
AMR_PILOT_SELECTED_SUBGRAPHS = os.path.join(AMR_PILOT, 'selected_subgraphs')

# maybe dict instead of set???
AMR_SPECIAL_CONCEPTS = { # excluding named entity related concepts
    # wh-words in wh-questions
    'amr-unknown',
    #amr-unintelligible,
    # ordinals
    'ordinal-entity',
    # named entities
    'name',
    # absolute time
    'date-entity', 'date-interval',
    # relative time
    # https://github.com/amrisi/amr-guidelines/blob/master/amr.md#quantities
    'monetary-quantity', 'distance-quantity', 'area-quantity',
    'volume-quantity', 'temporal-quantity', 'frequency-quantity',
    'speed-quantity', 'acceleration-quantity', 'mass-quantity',
    'force-quantity', 'pressure-quantity', 'energy-quantity',
    'power-quantity', 'voltage-quantity', 'charge-quantity',
    'potential-quantity', 'resistance-quantity', 'inductance-quantity',
    'magnetic-field-quantity', 'magnetic-flux-quantity',
    'radiation-quantity', 'concentration-quantity', 'temperature-quantity',
    'score-quantity', 'fuel-consumption-quantity', 'seismic-quantity',
    # mathematical operators
    'product-of', 'sum-of',
    # percentage
    'percentage-entity',
    # phone number
    'phone-number-entity',
    # email address
    'email-address-entity',
    # url
    'url-entity',
    }

NOMINATIVE_PRONOUNS = {
    'i', 'we',
    'you', "y'all",
    'he', 'she', 'it', 'they',
    'one',
    }
AMR_CONJUNCTIONS = {
    'and', 'or', 'either', 'neither',
    #'contrast-01',
    }

PREDICATE_NOUNS = { # followed by inverse core role events
    'thing', 'organization', 'person'
    }

DEIXIS = {
    'this','that','here','there'
    }
