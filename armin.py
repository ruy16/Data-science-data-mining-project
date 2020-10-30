from collections import defaultdict
from pandas import Series, DataFrame
from itertools import combinations
from itertools import permutations
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
    unverified_rules = dict()
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
    def rule_set_permutation(self, frequent_sets):
        for s in frequent_sets:
            p_set = list(permutations(s))
            for x in p_set:
                str_x = "".join(x)
                set_size = len(str_x)
                partition = ""
                for i in range(set_size-1):
                    partition += str_x[i]
                    partition = "".join(sorted(partition))
                    p_str = str_x[i+1:set_size]
                    p_str = "".join(sorted(p_str))
                    if partition not in self.unverified_rules:

                        self.unverified_rules[partition] = [p_str]
                    else:
                        if p_str not in self.unverified_rules[partition]:
                            self.unverified_rules[partition].append(p_str)

    # takes the unverified item sets count and filter
    def check_supp(self,unverified_count,sup_percent):
        verified_count = dict()
        for x in unverified_count:
            percentage = decimal.Decimal(format(unverified_count[x][1]/self.total_transaction_count,'.4f'))
            #print("!!!",percentage,sup_percent)
            if percentage.compare(decimal.Decimal(sup_percent)) != -1:
                #print("{l}>={r}".format(l=percentage,r=sup_percent))
                verified_count[x] = [percentage, unverified_count[x][1]]

        if len(verified_count.items()) == 0:
            return None
        return verified_count

    def check_confidence(self,unverified_rules,confidence):
        for key,value in unverified_rules.items():
            for i in value:
                rule_str = key +"=>" + i
                item_set = tuple(sorted(key+i))
                supp_percent = self.verified_frequent_set_final[item_set][0]
                union_count = self.verified_frequent_set_final[item_set][1]
                k = key
                if len(key) > 1:
                    k = tuple(sorted(key))
                conf = decimal.Decimal(format(union_count/self.verified_frequent_set_final[k][1],'.4f'))
                if conf.compare(decimal.Decimal(confidence)) != -1:
                    self.verified_rules.append(["R",supp_percent,conf,rule_str])

    # Counts the item set (unverified)
    def CFI(self,item_set):
        item_set_count = dict()
        for items in item_set:
            for trans_set in self.transaction_item_set:
                if 0 not in [c in trans_set for c in items]:
                    if items in item_set_count:
                        item_set_count[items][1] += 1
                    else:
                        item_set_count[items] = [0,1]
        return item_set_count

        # seriously adds comma between each char

    def add_comma_to_string(self, input_string):
        new_string = ""
        for i in range(len(input_string)):
            new_string += "," + input_string[i]
        return new_string

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
        self.verified_frequent_set_final.clear()
        self.verified_rules.clear()
        self.cfi_set.clear()
        self.single_item_count.clear()
        self.base_verified_set.clear()
        self.total_transaction_count = 0
        self.unverified_rules.clear()
        self.unverified_counts.clear()
        self.verified_frequent_set_per_step.clear()
        self.transaction_item_set.clear()

        #individual items
        all_items = list()
        # Step one: Count CFI(1)
        with open(input_filename,newline='') as inputcsv:
            csvreader = csv.reader(inputcsv,delimiter=' ',quotechar='|')
            for row in csvreader:
                self.total_transaction_count += 1
                remove_digits = str.maketrans('', '', string.digits)
                items = row[0].replace(',','').translate(remove_digits)
                self.transaction_item_set.append(items)
                for i in items:
                    if i not in all_items:
                        all_items.append(i)

        # gets the first frequent set
        self.single_item_count.update(self.CFI(all_items))
        self.base_verified_set.update(self.check_supp(self.single_item_count,min_support_percentage))
        self.verified_frequent_set_per_step.update(self.base_verified_set)
        self.verified_frequent_set_final.update(self.base_verified_set)
        base_list = list(self.base_verified_set.keys())
        base_list.sort()
        #print("first frequent set", self.base_verified_set)
        #print("all transactions\n",self.transaction_item_set)


        # Done
        # Step two: Count to CFI(i) => EMPTY
        cfi_size = 2

        while True:
            # clean up the bins before every run
            if len(self.verified_frequent_set_per_step.items()) != 0:
                self.verified_frequent_set_per_step.clear()
            if len(self.unverified_counts.items()) != 0:
                self.unverified_counts.clear()
            # generate the sets
            self.item_set_combination(base_list, cfi_size)
            self.unverified_counts.update(self.CFI(self.cfi_set))
            # verify the sets
            result = self.check_supp(self.unverified_counts,min_support_percentage)
            # if no more frequent sets can be found
            if result is None:
                break
            # register the current step frequent count
            self.verified_frequent_set_per_step.update(result)
            # add the partial counts to the final count
            self.verified_frequent_set_final.update(self.verified_frequent_set_per_step)
            #print("verified {s}:\n".format(s=cfi_size), self.verified_frequent_set_per_step)

            # Generate rules
            self.rule_set_permutation(self.verified_frequent_set_per_step.keys())
            cfi_size += 1

        # verify rules
        #print("Unverified rules:",self.unverified_rules)
        #print("\n!!!File:\n",output_filename)
        #print("\nfinal set:\n",self.verified_frequent_set_final)
        self.check_confidence(self.unverified_rules,min_confidence)
        #print("\nFinal rules:\n",self.verified_rules)


        # Write to output file
        with open(output_filename,'w',newline='') as output_csv:
            #output_writer = csv.writer(output_csv,delimiter=' ')
            # write the frequent sets
            for key,value in self.verified_frequent_set_final.items():
                set_str = "".join(key)
                prepare_str = "S,{supp}{item_set}\n".format(supp=value[0],item_set=self.add_comma_to_string(set_str))
                #print("writting sets:",prepare_str)
                output_csv.writelines(prepare_str)
            # write the ass rules
            for value in self.verified_rules:
                left_str = self.add_comma_to_string(value[3].split('=>')[0])
                right_str = self.add_comma_to_string(value[3].split('=>')[1])
                prepare_str = "R,{supp},{conf}{l},'=>'{r}\n".format(supp=value[1],conf=value[2],l=left_str,r=right_str)
                #print("writing rules:",prepare_str)
                output_csv.writelines(prepare_str)


if __name__ == "__main__":
    armin = Armin()
    armin.apriori('input.csv', 'output.sup=0.5,conf=0.7.csv', 0.5, 0.7)
    armin.apriori('input.csv', 'output.sup=0.5,conf=0.8.csv', 0.5, 0.8)
    armin.apriori('input.csv', 'output.sup=0.6,conf=0.8.csv', 0.6, 0.8)