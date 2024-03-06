import numpy as np
import polars as pl

from kaggle_home_credit_risk_model_stability.libs.input.dataset import Dataset

class SetTypesStep:
    def __init__(self):
        self.column_to_type = {}
        
    def process_train_dataset(self, train_dataset, columns_info):
        for name, table in train_dataset.get_tables():
            for column in table.columns:
                if column in ("WEEK_NUM", "case_id", "MONTH", "num_group1", "num_group2", "target"):
                    self.column_to_type[column] = pl.Int64
                elif ("DATE" in columns_info.get_labels(column)):
                    self.column_to_type[column] = pl.Date
                elif ("CATEGORICAL" in columns_info.get_labels(column)):
                    self.column_to_type[column] = pl.String
                else:
                    self.column_to_type[column] = pl.Float32
        return self.process(train_dataset, columns_info)
    
    def process_test_dataset(self, test_dataset, columns_info):
        return self.process(test_dataset, columns_info)
    
    def process(self, dataset, columns_info):
        assert(type(dataset) is Dataset)
        for name, table in dataset.get_tables():
            dataset.set(name, self.process_table(table, columns_info))

        return dataset, columns_info
    
    def process_table(self, table, columns_info):
        for column in table.columns:
            assert column in self.column_to_type, "Unknown column: {}".format(column)
            table = table.with_columns(table[column].cast(self.column_to_type[column]))
            if ("DATE" in columns_info.get_labels(column)):
               table = table.with_columns(table[column].cast(pl.Int32))
        return table