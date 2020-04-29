import dtw
from distance import DistanceMeasure as dm
from dataset import ListDataset
from core import AppContext
import numpy as np
import random
import time


class Splitter:

    def __init__(self, node):
        self.num_children = None
        self.temp_exemplars = dict()
        self.node = node
        self.best_splits = dict()
        self.exemplars = None

    def split_data(self, sample: ListDataset, data_per_class: dict):
        start = time.clock()
        splits = dict()
        branch = 0
        r = None
        for key in data_per_class.keys():
            entry = data_per_class[key]
            lenght = entry.get_series_size() - 1
            if lenght < 0:
                continue
            else:
                r = random.randint(0, lenght)
                splits[branch] = ListDataset.ListDataset()
                self.temp_exemplars[branch] = np.asarray(entry.get_series(r))
                branch = branch + 1

        # this
        # get_series_size
        sample_size = sample.get_expected_size()
        for j in range(0, sample_size):
            temp_exemplar_list = self.get_list_from_dict(self.temp_exemplars)
            closest_branch = Splitter.find_closest_branch(sample.get_series(j), temp_exemplar_list)
            if closest_branch == -1:
                assert False
            splits[closest_branch].add_series(sample.get_class(j), sample.get_series(j))
        stop = time.clock()
        # print("[TIEMPO][SPLIT DATA]:", stop - start)
        return splits

    @staticmethod
    def find_closest_branch(query, e):
        return dm.DistanceMeasure.find_closest_nodes(query, e)

    def find_closest_branch_(self, query):
        return dm.DistanceMeasure.find_closest_nodes(query, self.exemplars)

    def get_best_splits(self):
        return self.best_splits

    def weighted_gini(self, parent_size, splits):
        wgini = 0.0
        for spt in splits.values():
            wgini = wgini + (spt.get_expected_size() / parent_size) * spt.gini()
        return wgini

    def find_best_splits(self, data):
        #start = time.clock()
        data_per_class = data.split_classes()
        best_weighted_gini = 1000000
        parent_size = data.get_expected_size()
        for i in range(0, AppContext.AppContext.num_candidates_per_split):
            start = time.clock()
            splits = self.split_data(data, data_per_class)
            stop = time.clock()
            print("[TIEMPO SPLIT DATA]", (stop - start))
            weighted_gini = self.weighted_gini(parent_size, splits)
            if weighted_gini < best_weighted_gini:
                best_weighted_gini = weighted_gini
                self.best_splits = splits
                self.exemplars = self.temp_exemplars

        self.num_children = self.best_splits.__len__()
        #stop = time.clock()
        #print("[TIEMPO][FIND BEST SPLITS]:", stop - start)
        return self.best_splits

    @staticmethod
    def get_list_from_dict(query: dict):
        lista = list()
        for entry in query.values():
            lista.append(entry)
        return lista
