import numpy as np
import polars as pl
import gc

from kaggle_home_credit_risk_model_stability.libs.input.dataset import Dataset

class MergeChunkedTablesStep:        
    def process_train_dataset(self, train_dataset_generator):
        yield self.process(train_dataset_generator)
        
    def process_test_dataset(self, test_dataset_generator):
        yield self.process(test_dataset_generator)
    
    def process(self, dataset_generator):
        datasets = []
        columns_info = None
        for dataset, ci in dataset_generator:
            datasets.append(dataset)
            columns_info = ci
            gc.collect()
        return pl.concat(datasets, how="vertical_relaxed"), columns_info