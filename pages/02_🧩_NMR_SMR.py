import os
import sys
import time
import math
import pathlib
import requests
import datetime
import pandas as pd
import streamlit as st

sys.path.append("..")
from data.dictionary import get_dictionary
INDICATOR_dict = get_dictionary('INDICATOR')
REF_AREA_dict = get_dictionary('REF_AREA')

# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

# Streamlit set_page_config method has a 'initial_sidebar_state' argument that controls sidebar state.
st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state, layout="wide")

# Show title and description of the app.
st.title("SMR/NMR Study")
st.sidebar.write("""
**Sidebar**

Use the checkbox to preview dataframes before rendering any visualzations.

""")

with st.sidebar:
    fetch_from_cloud = st.radio(
    "Fetch data from github?",
    ('No', 'Yes'))

if fetch_from_cloud == 'Yes':
    link_prefix = "https://raw.githubusercontent.com/harry-oestreicher/umr_eda/main/data/"
else:
    link_prefix = "data/"

data_links = {
    "indicator": {
        "NMR_SMR_": link_prefix + "nmr_smr_merged.csv",
    },
}

@st.cache_data
def get_indicator_data(url):
    df = pd.read_csv(url)
    df.drop(columns=["Unnamed: 0"], inplace=True)
    return df

def get_indicator_dict(name):
    in_csv = os.path.join(os.getcwd(), "data/umr_data_dict_INDICATOR.csv")
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

def app():
    st.write(
        """
        Net migration rate and suicide mortality rate analysis.
        """
    )

    st.write("---")
    st.write("https://raw.githubusercontent.com/harry-oestreicher/umr_eda/main/data/nmr_smr_merged.csv")

    df = get_indicator_data(data_links["indicator"]["NMR_SMR_"])
    sorted = df.sort_values(by=["REF_AREA", "TIME_PERIOD"]).copy()
    sorted = sorted.replace({"REF_AREA": REF_AREA_dict}).copy()

    show_tables = "no"
    show_tables = st.checkbox("Show Dataframes")
    if show_tables:
        row1a_col1, row1a_col2 = st.columns([4, 4])
        with row1a_col1:
            st.write(sorted)
        with row1a_col2:
            st.write(".")

    chart_data = sorted[['REF_AREA', 'TIME_PERIOD', 'AGE_x','SMR','RANK','AGE_y','NMR']].sort_values('REF_AREA').copy()
    chart_data.rename(columns={
        "REF_AREA": "Country", 
        "AGE_x": "NMR Age",
        "AGE_y": "SMR Age",
        "NMR": "Net Migration Rate",
        "SMR": "Suicide/Mortality Rate",
    }, inplace=True)

    st.line_chart(chart_data, y=["Net Migration Rate", "Suicide/Mortality Rate" ], x='Country', height=500)

app()
