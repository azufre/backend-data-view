# Data Analysis App with Polars

The data analysis app is designed to perform statistical calculations, specifically calculating the mean and standard deviation, using the powerful Polars library. The app reads data from a CSV file, processes it using Polars, and provides users with insights into the dataset.

## Key Features:

- **Mean Calculation:** The app calculates the mean value for each numerical column in the dataset by grouping the data based on a specified categorical column, often referred to as the "class."

- **Standard Deviation Calculation:** Additionally, the app computes the standard deviation for each numerical column, also grouped by the categorical column, enabling users to understand the data's dispersion and variability.

## Data Processing:

- **Polars Library:** The app leverages the Polars library for efficient and scalable data processing. Polars provides a DataFrame-like data structure, LazyFrame, enabling fast and parallelized computations on large datasets.

- **Reading from CSV:** The app reads data from a CSV file, transforming it into a LazyFrame to handle large datasets without loading everything into memory at once.

## Usage:

- **Data Analysis:** Users can interact with the app through a user-friendly interface to analyze their datasets conveniently. The app requires users to specify the CSV file's path, and it automatically calculates the mean and standard deviation of the numerical columns, grouped by the specified categorical column.

## Benefits:

- **Speed:** Polars is a high-performance library, ensuring that data analysis on large datasets is swift and efficient, providing quick results.

- **Memory Efficiency:** The LazyFrame's laziness allows the app to handle enormous datasets without consuming excessive memory.

- **Customization:** Users have the flexibility to choose their desired CSV file and the categorical column for grouping, enabling them to perform specific analyses on their datasets.

Overall, the data analysis app using Polars and CSV input simplifies the process of calculating the mean and standard deviation, empowering users to gain insights into their data, make data-driven decisions, and perform statistical analysis with ease.

# Running FastAPI App Using Docker Compose

**Command:** `docker-compose up`

**Explanation:** This command builds the Docker image from the Dockerfile, creates a container, and runs your FastAPI app inside the container. The app will be accessible at `http://localhost:8000`.

# Running Unit Tests

**Command (pytest):** `pytest`

**Explanation:** This command executes the unit tests written in your FastAPI app. It uses the `pytest` testing framework to discover and run the test cases.

**Command (unittest):** `python -m unittest discover`

**Explanation:** This command executes the unit tests written in your FastAPI app. It uses the built-in `unittest` framework to discover and run the test cases.
