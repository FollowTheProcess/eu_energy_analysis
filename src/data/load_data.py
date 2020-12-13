"""
Simple class based thing to make loading the datasets nice and easy.

Author: Tom Fleet
Created: 13/12/2020
"""

import pandas as pd
from sqlalchemy import MetaData, create_engine

from src.config import RAW_DATA


class Data:
    def __init__(self, dataset: str) -> None:
        """
        Simple class to act as an API for loading the data
        into a pandas dataframe.

        Args:
            dataset (str): One of 'generation_capacity' or 'time_series'.

        Raises:
            ValueError: If invalid argument passed to dataset.
        """
        self.dataset = dataset.lower().strip()

        if self.dataset == "generation_capacity":
            self._fp = RAW_DATA.joinpath("national_generation_capacity.sqlite")
            self._tablename = "national_generation_capacity_stacked"

        elif self.dataset == "time_series":
            self._fp = RAW_DATA.joinpath("time_series.sqlite")
            self._tablename = "time_series_60min_singleindex"

        else:
            raise ValueError(
                f"""Argument 'dataset' should be one of 'generation_capacity' or 'time_series'.
                Got {self.dataset}"""
            )

        # So SQLAlchemy knows all the schema and metadata for our tables
        # Not essential but tends to come in handy
        self._engine = create_engine(f"sqlite:///{str(self._fp)}")
        self._meta = MetaData(bind=self._engine)
        self._meta.reflect()
        self._table = self._meta.tables[self._tablename]

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(dataset={self.dataset!r})"

    def load_table(self) -> pd.DataFrame:
        """
        Loads the entire SQL table into a pandas dataframe.

        Uses a hardcoded table name. In the case of the National Generation
        Capacity data there is only one table 'national_generation_capacity_stacked'

        The time series data has 3 tables with different time deltas as the index
        either 60 mins, 30 mins, or 15 mins. I've chosen the 60 min one as the default
        table to load here.

        Returns:
            pd.DataFrame: DataFrame containing the table data.
        """

        return pd.read_sql_table(table_name=self._tablename, con=self._engine)


class GenerationCapacity(Data):
    def __init__(self, dataset: str = "generation_capacity") -> None:
        super().__init__(dataset=dataset)

    def load_cleaned(self) -> pd.DataFrame:
        """
        Loads the Generation Capacity data in it's cleaned form.

        Returns:
            pd.DataFrame: Cleaned generation capacity data.
        """

        df = (
            (self.load_table())
            .assign(
                technology=lambda x: pd.Categorical(x["technology"]),
                source=lambda x: pd.Categorical(x["source"]),
                source_type=lambda x: pd.Categorical(x["source_type"]),
                country=lambda x: pd.Categorical(x["country"]),
                capacity_definition=lambda x: pd.Categorical(x["capacity_definition"]),
            )
            .drop(columns=["weblink", "type", "comment"])
            .dropna()
        )

        return df
