"""
Script to download the Open Power System Data.

Will download the sqlite databases of the national generation capacity
and the time series datasets and save to Data/Raw.

Author: Tom Fleet
Created: 13/12/2020
"""

import shutil

import requests

from src.config import CAPACITY_URL, RAW_DATA, TIME_SERIES_URL


def fetch_dataset(dataset: str) -> None:
    """
    Downloads the chosen dataset from the Open Power System database.

    Args:
        dataset (str): Name of dataset. One of either 'generation_capacity'
            or 'time_series'

    Raises:
        ValueError: If invalid dataset passed.

    Returns:
        None
    """

    if dataset.lower().strip() == "generation_capacity":
        url = CAPACITY_URL
    elif dataset.lower().strip() == "time_series":
        url = TIME_SERIES_URL
    else:
        raise ValueError(
            f"""Argument 'dataset' should be one of 'generation_capacity' or 'time_series'.
            Got {dataset}"""
        )

    local_filename = url.split("/")[-1]
    local_path = RAW_DATA.joinpath(local_filename)

    if not local_path.exists():

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)

        print(f"Downloaded {dataset}, saved to {str(local_path)}")

    else:
        print(f"File {str(local_path)} already exists!")

    return None


if __name__ == "__main__":
    fetch_dataset(dataset="generation_capacity")
    fetch_dataset(dataset="time_series")
