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

        self._engine = create_engine(f"sqlite:///{str(self._fp)}")

        # So SQLAlchemy knows all the schema and metadata for our tables
        # Not essential but tends to come in handy
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
    def __init__(self) -> None:
        super().__init__(dataset="generation_capacity")

    def load_cleaned(self, level: str = None) -> pd.DataFrame:
        """
        Loads the cleaned Generation Capacity dataset into a pandas dataframe.

        User can specify the energy_source_level using the 'level' argument.

        If no level is passed, the entire dataset will be loaded.

        If level is passed, the energy source level columns will be dropped on load
        as they are no longer needed.

        Args:
            level (str, optional): Level to load, one of ['total', 'type', 'fuel'].
                'total' refers to energy_source_level_0
                'type' is energy_source_level_1
                'fuel' is energy_source_level_2
                If None: loads entire dataset
                Defaults to None.

        Raises:
            ValueError: If passed level not in ['total', 'type', 'fuel']

        Returns:
            pd.DataFrame: Dataframe containing requested data.
        """

        levels = {
            "total": "energy_source_level_0",
            "type": "energy_source_level_1",
            "fuel": "energy_source_level_2",
        }

        df = (
            (self.load_table())
            .assign(
                technology=lambda x: pd.Categorical(x["technology"]),
                country=lambda x: pd.Categorical(x["country"]),
                year=lambda x: pd.to_datetime(x["year"], format=r"%Y"),
            )
            .drop(
                columns=[
                    "ID",
                    "weblink",
                    "type",
                    "comment",
                    "capacity_definition",
                    "source",
                    "source_type",
                ]
            )
            .drop_duplicates(
                subset=["technology", "year", "country"],
                keep="first",
                ignore_index=True,
            )
            .replace(to_replace="Other or unspecified energy sources", value="Other")
            .replace(to_replace="Renewable energy sources", value="Renewables")
            .dropna()
        )

        if level is not None and level not in levels.keys():
            raise ValueError(
                f"Passed level must be one of ['total', 'type', 'fuel']. Got {level}"
            )
        elif level is None:
            return df
        else:
            return df[df[levels.get(level)] == 1].drop(
                columns=[
                    "energy_source_level_0",
                    "energy_source_level_1",
                    "energy_source_level_2",
                    "energy_source_level_3",
                    "technology_level",
                ]
            )

    def load_top5(self) -> pd.DataFrame:
        """
        Loads the Generation Capacity for the top 5 highest capacity
        countries.

        Returns:
            pd.DataFrame: Top 5 countries generation capacity data.
        """

        df = self.load_cleaned()

        top5_countries = ["FR", "DE", "IT", "ES", "GB"]

        df = df[df["country"].isin(top5_countries)]

        return df

    def load_uk(self) -> pd.DataFrame:
        """
        Loads the UK generation capacity data.

        Returns:
            pd.DataFrame: UK Data.
        """

        df = self.load_cleaned()

        df = df[df["country"] == "UK"]

        return df


class TimeSeries(Data):
    def __init__(self, dataset: str = "time_series") -> None:
        super().__init__(dataset=dataset)
