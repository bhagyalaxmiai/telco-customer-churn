import logging
import os
import pandas as pd
from pandas import DataFrame
from source.exception import ChurnException
from pymongo.mongo_client import MongoClient
from sklearn.model_selection import train_test_split
from source.logger import logging


class DataIngestion:

    def __init__(self, train_config) -> DataFrame:
        self.train_config = train_config

    def export_data_into_feature_store(self):
        try:
            logging.info("start : data load from mongodb")
            # mongodb_url = self.train_config.mongodb_url_key
            # database = self.train_config.database_name
            # collection = self.train_config.collection_name

            client = MongoClient(self.train_config.mongodb_url_key)
            database = client[self.train_config.database_name]
            collection = database[self.train_config.collection_name]

            cursor = collection.find()

            data = pd.DataFrame(list(cursor))

            dir_path = os.path.dirname(self.train_config.feature_store_dir_path)
            # print(f"feature_store_file_path {dir_path}")
            os.makedirs(dir_path, exist_ok=True)  # if not exist then create
            data.to_csv(self.train_config.feature_store_dir_path, index=False)

            logging.info("Complete : data load from mongodb")

            return data

        except ChurnException as e:
            logging.error(e)
            raise e

    def split_data_test_train(self, data: DataFrame) -> None:
        try:
            logging.info("start: train, test data split")
            train_set, test_set = train_test_split(data, test_size=self.train_config.train_test_split_ratio)
            dir_path = os.path.dirname(self.train_config.train_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_set.to_csv(self.train_config.train_file_path, index=False)
            test_set.to_csv(self.train_config.test_file_path, index=False)

            logging.info("complete: train, test data split")
        except ChurnException as e:
            raise e

    def initiate_data_ingestion(self):
        data = self.export_data_into_feature_store()
        self.split_data_test_train(data)
