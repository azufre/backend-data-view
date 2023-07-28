import io
import os
import polars as pl
from fastapi_cache.decorator import cache

class DataService:
    """
    A service class to handle data processing and caching operations.

    Attributes:
    - csv_file_path (str): The path to the CSV file containing raw data.
    - parquet_file_path (str): The path to the Parquet file used for caching processed data.

    Methods:
    - convert_csv_to_parquet(source_file: str, target_file: str) -> None:
        Reads data from a CSV file and writes it to a Parquet file.

    - clean_data(df: pl.DataFrame) -> pl.DataFrame:
        Cleans the input DataFrame by filling NaN values with None and dropping rows with null values.

    - get_data_from_memory() -> pl.DataFrame:
        Retrieves the data from the CSV file, stores it in memory using caching, 
        cleans the data, and returns the processed DataFrame.

    - get_data_from_file() -> pl.LazyFrame:
        Retrieves the data from the Parquet file using caching. 
        If the file does not exist, 
        it converts the CSV file to Parquet and returns the lazy DataFrame.

    """

    def __init__(self) -> None:
        """
        Initializes the DataService with file paths for CSV and Parquet files.

        The file paths are determined using the environment variables "csv_file_path" and "parquet_file_path".

        Returns:
        None
        """
        self.csv_file_path = os.path.join(os.path.dirname(__file__), os.environ.get("csv_file_path"))
        self.parquet_file_path = os.path.join(os.path.dirname(__file__), os.environ.get("parquet_file_path"))

    def convert_csv_to_parquet(self, source_file: str, target_file: str) -> None:
        """
        Reads data from a CSV file and writes it to a Parquet file.

        Parameters:
        - source_file (str): The path to the CSV file.
        - target_file (str): The path to the Parquet file.

        Returns:
        None
        """
        df: pl.DataFrame = pl.read_csv(source_file)
        df.write_parquet(target_file)

    def clean_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Cleans the input DataFrame by filling NaN values with 
        None and dropping rows with null values.

        Parameters:
        - df (pl.DataFrame): The input DataFrame.

        Returns:
        pl.DataFrame: The cleaned DataFrame.
        """
        df = df.fill_nan(None).drop_nulls()
        return df

    @cache(expire=600)
    def get_data_from_memory(self) -> pl.DataFrame:
        """
        Retrieves the data from the CSV file, stores it in memory using caching, 
        cleans the data, and returns the processed DataFrame.

        The data is cached for 600 seconds (10 minutes) 
        to reduce file I/O overhead for subsequent calls.

        Returns:
        pl.DataFrame: The processed DataFrame containing data from the CSV file.
        """
        buffer = io.BytesIO()
        df: pl.DataFrame = pl.read_csv(self.csv_file_path)
        df.write_parquet(buffer)
        buffer.seek(0)
        lazy_df: pl.DataFrame = pl.read_parquet(buffer, use_pyarrow=True)
        lazy_df = self.clean_data(lazy_df)
        return lazy_df

    @cache(expire=600)
    def get_data_from_file(self) -> pl.LazyFrame:
        """
        Retrieves the data from the Parquet file using caching. 
        If the file does not exist, it converts the CSV file to Parquet 
        and returns the lazy DataFrame.

        The data is cached for 600 seconds (10 minutes) to reduce file I/O overhead for subsequent calls.

        Returns:
        pl.LazyFrame: The lazy DataFrame containing data from the Parquet file.
        """
        if not os.path.exists(self.parquet_file_path):
            self.convert_csv_to_parquet(self.csv_file_path, self.parquet_file_path)
        lazy_df: pl.LazyFrame = pl.scan_parquet(self.parquet_file_path)
        return lazy_df
