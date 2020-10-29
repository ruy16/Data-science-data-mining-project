from collections import defaultdict
from pandas import Series, DataFrame
from itertools import combinations
import itertools as it
import pandas as pd
import math
import csv
import sys
import argparse
import collections
import glob
import os
import re
import requests
import string
import sys
import decimal


class Armin():
    # number total transactions
    total_transaction_count = 0
    # All the item sets
    transaction_item_set = list()

    # all possible combination of last cfi frequent set
    cfi_set = list()
    #base verified set
    base_verified_set = dict()
    # unverified frequent sets
    unverified_counts = dict()
    # verified frequent sets per step
    verified_frequent_set_per_step = dict()
    # final frequent set
    verified_frequent_set_final = dict()

    # all possible rules of last frequent set
    unverified_rules = list()
    # verified association rules
    verified_rules = list()

    # cfi(1) item count
    single_item_count = dict()

    # generate all possible item sets
    def item_set_combination(self, frequent_set, size):
        # put the new item set in cfi_set
        self.cfi_set.clear()
        self.cfi_set.extend(combinations(frequent_set, size))


    # generate all possible rules
    def rule_set_permutation(self, frequent_set):

        pass

    # takes the unverified item sets count and filter
    def check_supp(self,sup_percent):
        if len(self.verified_frequent_set_per_step.items()) != 0:
            self.verified_frequent_set_per_step.clear()
        for x in self.unverified_counts:
            percentage = decimal.Decimal(format(self.unverified_counts[x][1]/self.total_transaction_count,'.4f'))
            if percentage >= sup_percent:
                self.verified_frequent_set_per_step[x]= [percentage, self.unverified_counts[x][1]]
        self.verified_frequent_set_final.update(self.verified_frequent_set_per_step)

        if len(self.verified_frequent_set_per_step.items()) == 0:
            return None
        return 1

    def check_confidence(self,confidence):
        for x in self.verified_frequent_set_per_step:
            pass

    # Counts the item set (unverified)
    def CFI(self):
        if len(self.unverified_counts.items()) != 0:
            self.unverified_counts.clear()
        for item_set in self.cfi_set:
            for trans_set in self.transaction_item_set:
                if 0 not in [c in trans_set for c in item_set]:
                    if item_set in self.unverified_counts:
                        self.unverified_counts[item_set][1] += 1
                    else:
                        self.unverified_counts[item_set] = [0,1]


    def apriori(self, input_filename, output_filename, min_support_percentage, min_confidence):
        """
        Implement the Apriori algorithm, and write the result to an output file

        PARAMS
        ------
        input_filename: String, the name of the input file
        output_filename: String, the name of the output file
        min_support_percentage: float, minimum support percentage for an itemset
        min_confidence: float, minimum confidence for an association rule to be significant

        """


        # Step one: Count CFI(1)
        with open(input_filename,newline='') as inputcsv:
            csvreader = csv.reader(inputcsv,delimiter=' ',quotechar='|')
            for row in csvreader:
                self.total_transaction_count += 1
                remove_digits = str.maketrans('', '', string.digits)
                items = row[0].replace(',','').translate(remove_digits)
                self.transaction_item_set.append(items)
                for item in items:
                    if item in self.single_item_count:
                        self.single_item_count[item][1] += 1
                    else:
                        self.single_item_count[item] = [0,1]
        self.unverified_counts = self.single_item_count
        self.check_supp(min_support_percentage)
        self.base_verified_set.update(self.verified_frequent_set_per_step)
        base_list = list(self.base_verified_set.keys())
        base_list.sort()

        print("first frequent set", self.base_verified_set)
        print("all transactions\n",self.transaction_item_set)
        #print(self.verified_rules)

        # Done
        # Step two: Count to CFI(i) => EMPTY
        cfi_size = 2

        while True:
            self.item_set_combination(base_list, cfi_size)
            self.CFI()
            if self.check_supp(min_support_percentage) is None:
                break
            print("verified {s}:\n".format(s=cfi_size), self.verified_frequent_set_per_step)
            # Generate rules
            self.rule_set_permutation(self.verified_frequent_set_per_step.keys())
            self.check_confidence(min_confidence)
            cfi_size += 1

        print("final set:",self.verified_frequent_set_final)

        print(self.verified_rules)


if __name__ == "__main__":
    armin = Armin()
    armin.apriori('input.csv', 'output.sup=0.5,conf=0.7.csv', 0.5, 0.7)
    #armin.apriori('input.csv', 'output.sup=0.5,conf=0.8.csv', 0.5, 0.8)
    #armin.apriori('input.csv', 'output.sup=0.6,conf=0.8.csv', 0.6, 0.8)