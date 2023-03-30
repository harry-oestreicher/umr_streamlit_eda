import datetime
import os
import sys
import time
import math
import pathlib
import requests
# import zipfile
import pandas as pd
# import pydeck as pdk
# import geopandas as gpd
import streamlit as st
# import leafmap.colormaps as cm
# from leafmap.common import hex_to_rgb
# from pydeck.types import String

import hvplot.pandas
import panel as pn
import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

sys.path.append("..")
from src.data.dictionary import get_dictionary
INDICATOR_dict = get_dictionary('INDICATOR')

# # load the world dataset
# world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
# cities = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))


# Begin Streamlit
# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

# Streamlit set_page_config method has a 'initial_sidebar_state' argument that controls sidebar state.
st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state, layout="wide")

# Show title and description of the app.
st.title("Net Migration Rate 2021")
st.sidebar.write("""
**Sidebar**

`pydeck` is used to manage layers and enumeration in some cases.

Use the filter dropdowns to alter your results.

Use the checkbox to preview data before map rendering.

""")


link_prefix = "https://raw.githubusercontent.com/harry-oestreicher/umr_eda/main/data/umr/"

data_links = {
    "reference": {
        "countries": link_prefix + "umr_eda_NMR.csv", # <== Net Migration
        "countries_hires": link_prefix + "umr_eda_NMR.csv", # <== Net Migration
    },
    "indicator": {
        "_ALL_": link_prefix + "all_indicators_2012-2022.csv",
        "DM_": link_prefix + "umr_data_DM_.csv",
        "ECON_": link_prefix + "umr_data_ECON_.csv",
        "MG_": link_prefix + "umr_data_MG_.csv",
        "MNCH_": link_prefix + "umr_data_MNCH_.csv",
        "PT_": link_prefix + "umr_data_PT_.csv",
        "PV_": link_prefix + "umr_data_PV_.csv",
        "WS_": link_prefix + "umr_data_WS_.csv",
    },
}

def get_data_columns(df, category="world", frequency="annual"):
    cols = df.columns.values.tolist()
    return cols[1:]

@st.cache_data
def get_reference_data(url):
    df = pd.read_csv(url)
    df.drop(columns=["Unnamed: 0", "AGE"], inplace=True)
    df = df[df.TIME_PERIOD==2021]
    return df

@st.cache_data
def get_indicator_data(url):
    df = pd.read_csv(url)
    df.drop(columns=["Unnamed: 0"], inplace=True)
    df = df[df.TIME_PERIOD==2021]
    return df

def get_indicator_dict(name):
    in_csv = os.path.join(os.getcwd(), "src/data/umr/umr_data_dict_INDICATOR.csv")
    df = pd.read_csv(in_csv)
    value = df[df.key==name]["value"].values[0]
    return value

def enumerate_column(col_in):
    if col_in == "REF_AREA":
        REF_AREA = REF_AREA_dict
        val = REF_AREA.get(col_in)

    elif col_in == "INDICATOR":
        INDICATOR = INDICATOR_dict
        val = INDICATOR.get(col_in)
    return val

def get_indicators(df):
    indicator_list = df["INDICATOR"].unique()
    return indicator_list

def app():
    # st.title("Unaccompanied Minor Research")
    st.write(
        """
        ### Exploratory Data Analysis

        Test
          
        """
    )

    row1_col1, row1_col2, row1_col3  = st.columns(
        [1,1,6]
    )

    years_list = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]

    with row1_col1:
        # st.write("**Year: 2021**")
        selected_year = st.selectbox("**Year**", years_list )

    # with row1_col2:
        # indicator = st.selectbox("**Risk Factor Group**", ["DM_", "ECON_", "MG_", "MNCH_", "PT_", "WS_"])

    # manually setting these for now
    frequency = "annual"
    scale = "countries"

    indicator_df = get_indicator_data(data_links["indicator"]["_ALL_"])

    with row1_col3:
        selected_col = "OBS_VALUE" #st.selectbox("Attribute", data_cols, 4)
        # st.write(indicator_df.head(3))
        this_ind_list = indicator_df["INDICATOR"].unique().tolist()
        this_indicator = st.selectbox("**Indicator:**", this_ind_list)
        this_indicator_text = get_indicator_dict(this_indicator)
        # Display the indicator full text
        st.write(this_indicator_text)
        # st.write(indicator_df["OBS_VALUE"].dtype)


    show_tables = "no"
    show_tables = st.checkbox("Show Dataframe")

    row1a_col1, row1a_col2 = st.columns([4, 4])

    if show_tables:
        # with row1a_col1:
        st.write(indicator_df)

        # with row1a_col2:
        #     indicator_data_cols = get_data_columns(inventory_df, scale.lower(), frequency.lower())
        #     indicator_df = indicator_df[indicator_df.INDICATOR==this_indicator]
        #     st.write(f"#### {this_indicator} Layer")
        #     st.write(indicator_df)

    chart_df = indicator_df.copy()

    # nice_plot = chart_df.hvplot.line(x="REF_AREA", y="OBS_VALUE", by="TIME_PERIOD", rot=55, title=str(selected_year))
    nice_plot = chart_df.hvplot.line(x="REF_AREA", y="OBS_VALUE", by="TIME_PERIOD", rot=55, width=1000, height=500)
    st.write(hv.render(nice_plot, backend='bokeh'))

    # def show_chart(value):
    #     mydata = chart_df[chart_df.TIME_PERIOD==value].hvplot.line(x="REF_AREA", y="OBS_VALUE", by="TIME_PERIOD", rot=55, title=value)
    #     # pane = pn.panel(mydata)
    #     return pane

    # ind = "Indicator Comparison preview"
    # # chart_df = chart_df[chart_df.loc[:, 'OBS_VALUE'] > 30]

    # ind_list = chart_df["INDICATOR"].unique()

    # show_chart(selected_year)

    # return None

app()
