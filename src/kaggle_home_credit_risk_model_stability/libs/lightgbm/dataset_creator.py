import lightgbm as lgb

import polars as pl

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
    
class LightGbmDatasetCreator:
    def __init__(self, dataset_params, chunk_size = 100):
        self.dataset_params = dataset_params
        self.chunk_size = chunk_size

    def create(self, dataframe):
        chunk_size = 100
        columns = dataframe.columns
        columns.remove("target")

        dataframe_categorical_features = [feature for feature in columns if dataframe[feature].dtype == pl.Enum]
        X = dataframe[columns]
        Y = dataframe["target"]
        
        dataset = None
        for chunk_index, columns_chunk in enumerate(chunker(columns, chunk_size)):
            chunk_categorical_features = [feature for feature in columns_chunk if X[feature].dtype == pl.Enum]
    
            physical_X = X[columns_chunk].with_columns(*[
                pl.col(column).to_physical()
                for column in chunk_categorical_features
            ])
    
            data = lgb.Dataset(
                physical_X.to_numpy(),
                Y.to_numpy(),
                params=self.dataset_params,
                categorical_feature=chunk_categorical_features,
                feature_name=physical_X.columns,
                free_raw_data=False
            )

            data.construct()
            if dataset is None:
                dataset = data
            else:
                dataset.add_features_from(data)
                
        dataset.set_categorical_feature(dataframe_categorical_features)
        return dataset