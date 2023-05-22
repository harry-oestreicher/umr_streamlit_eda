import os
import sys
import time
import math
import pathlib
import requests
import datetime
import pandas as pd
import streamlit as st
import hvplot.pandas
import panel as pn
import holoviews as hv
import bokeh.plotting
import streamlit_toggle as tog

from holoviews import opts
# hv.extension('bokeh', logo=False)
from bokeh.models.formatters import NumeralTickFormatter

num_formatter = NumeralTickFormatter(format="0,0")

sys.path.append("..")
from data.dictionary import get_dictionary
INDICATOR_dict = get_dictionary('INDICATOR')
REF_AREA_dict = get_dictionary('REF_AREA')

# Begin Streamlit
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
    Toggle = tog.st_toggle_switch(label="fetch data from cloud", 
                key=True, 
                default_value=False, 
                label_after = False, 
                inactive_color = '#D3D3D3', 
                active_color="#11567f", 
                track_color="#29B5E8"
                )

if Toggle == True:
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
    # df = df[df["TIME_PERIOD"] >= 2011].copy()
    df.drop(columns=["Unnamed: 0"], inplace=True)
    # df.replace({"INDICATOR": INDICATOR_dict}, inplace=True)
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

# def get_indicators(df):
#     indicator_list = df["INDICATOR"].unique()
#     return indicator_list

def app():
    # st.title("Unaccompanied Minor Research")
    st.write(
        """
        ### Exploratory Data Analysis
        
        """
    )

    st.write("---")
    st.write("https://raw.githubusercontent.com/harry-oestreicher/umr_eda/main/data/nmr_smr_merged.csv")

    df = get_indicator_data(data_links["indicator"]["NMR_SMR_"])
    sorted = df.sort_values(by=["REF_AREA", "TIME_PERIOD"]).copy()
    sorted = sorted.replace({"REF_AREA": REF_AREA_dict}).copy()

    # sorted["SMR"] = sorted.groupby("TIME_PERIOD")['SMR'].transform("mean")

    show_tables = "no"
    show_tables = st.checkbox("Show Dataframes")
    if show_tables:
        row1a_col1, row1a_col2 = st.columns([4, 4])
        with row1a_col1:
            st.write(sorted)
        with row1a_col2:
            st.write(".")

    nice_plot1 = sorted.hvplot.line(x="REF_AREA", y=["NMR", "SMR"], legend=True, rot=85, width=1100, height=600)
    # nice_plot2 = top_40_merged[top_40_merged.INDICATOR==this_indicator].hvplot.scatter(y="OBS_VALUE", x="REF_AREA", by="TIME_PERIOD", rot=45, width=1000, height=500, yformatter=num_formatter, ylabel="Observation Value", xlabel="Top-N Countries", title=this_indicator )
    # # st.write("### Top NMR Countries Indicator Comparison")
    st.write(hv.render(nice_plot1, backend='bokeh'))

app()
