# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pathlib import Path
from csv import writer
from sqlalchemy import inspect, engine, create_engine, Table

# Establish and define database connection
umr_connection_string = 'sqlite:///./src/data/umrdata.db'
engine = create_engine(umr_connection_string)
insp = inspect(engine)

def get_all_table_names():
    mystr = insp.get_table_names()
    return mystr

def init_umr_data():
    # Initialization data
    umr_df = pd.read_csv(Path("./src/data/global_migrant_decades_EDA3_filter-PV_CHLD_2023-02-05_15-09-47.csv"), index_col=False)
    indicator_df = pd.read_csv(Path("./src/data/global_migrant_decades_LOOKUP_INDICATOR.csv"), index_col=False)
    ref_area_df = pd.read_csv(Path("./src/data/global_migrant_decades_LOOKUP_REF_AREA.csv"), index_col=False)
    age_df = pd.read_csv(Path("./src/data/global_migrant_decades_LOOKUP_AGE.csv"), index_col=False)

    # Write data to sql tables
    umr_df.to_sql('UMR', engine, index=False, if_exists='replace')
    indicator_df.to_sql('UMR_INDICATOR', engine, index=False, if_exists='replace')
    ref_area_df.to_sql('UMR_REF_AREA', engine, index=False, if_exists='replace')
    age_df.to_sql('UMR_AGE', engine, index=False, if_exists='replace')

    # umr_df.drop(columns=["INDEX"], inplace=True)
    # indicator_df.drop(columns=["INDEX"], inplace=True)
    # ref_area_df.drop(columns=["INDEX"], inplace=True)

    return None

def get_umr_data(query):
    df = pd.read_sql_query(query, con=engine)
    return df
