import os
import unittest
import polars as pl
from services.data_service import DataService

class DataServiceMock(DataService):

    def __init__(self, csv_file_path: str, parquet_file_path: str) -> None:
        super().__init__()

        self.csv_file_path = csv_file_path
        self.parquet_file_path = parquet_file_path

class TestDataService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store test data files
        cls.temp_dir = os.path.join(os.path.dirname(__file__), "temp_data")
        os.makedirs(cls.temp_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory and its contents after the tests
        import shutil
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        # Create an instance of DataService for testing
        self.data_service = DataServiceMock(
            os.path.join(self.temp_dir, "test_data.csv"),
            os.path.join(self.temp_dir, "test_data.parquet")
        )

    def tearDown(self):
        # Clean up any resources after each test method runs
        pass

    def test_convert_csv_to_parquet(self):
        # Define the test CSV file and target Parquet file paths
        source_file = os.path.join(self.temp_dir, "test_data.csv")
        target_file = os.path.join(self.temp_dir, "test_data.parquet")

        # Create a sample CSV file (you can modify this for relevant test data)
        with open(source_file, "w") as f:
            f.write("class,feature1,feature2\n1,10,100\n1,20,200\n2,30,300\n2,40,400\n")

        # Call the convert_csv_to_parquet method
        self.data_service.convert_csv_to_parquet(source_file, target_file)

        # Assert that the target Parquet file is created
        self.assertTrue(os.path.exists(target_file))

        # Clean up the created files
        os.remove(source_file)
        os.remove(target_file)

    def test_clean_data(self):
        # Create a sample DataFrame for testing
        data = {
            "class": [1, 2, None, 3],
            "feature1": [10, None, 30, 40],
            "feature2": [None, 200, 300, 400],
        }
        df = pl.DataFrame(data)

        # Call the clean_data method
        cleaned_df = self.data_service.clean_data(df)

        # Assert that the DataFrame is cleaned (no null values)
        self.assertEqual(cleaned_df.shape[0], 1)

    async def test_get_data_from_memory(self):
        # Call the get_data_from_memory method
        df = await self.data_service.get_data_from_memory()

        # Assert that the returned DataFrame is of type pl.LazyFrame
        self.assertIsInstance(df, pl.LazyFrame)

    async def test_get_data_from_file(self):
        # Call the get_data_from_file method
        df = await self.data_service.get_data_from_file()

        # Assert that the returned DataFrame is of type pl.LazyFrame
        self.assertIsInstance(df, pl.LazyFrame)