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

from holoviews import opts
hv.extension('bokeh')

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
st.title("Net Migration Rate")
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

# def get_data_columns(df, category="world", frequency="annual"):
#     cols = df.columns.values.tolist()
#     return cols[1:]

# @st.cache_data
# def get_reference_data(url):
#     df = pd.read_csv(url)
#     df.drop(columns=["Unnamed: 0", "AGE"], inplace=True)
#     df = df[df.TIME_PERIOD==2021]
#     return df

# @st.cache_data
# def get_data(url):
#     df = pd.read_csv(url)
#     df.drop(columns=["Unnamed: 0"], inplace=True)
#     # df = df[df.TIME_PERIOD==2021]
#     return df

@st.cache_data
def get_indicator_data(url):
    df = pd.read_csv(url)
    df.drop(columns=["Unnamed: 0"], inplace=True)
    # df = df[df.TIME_PERIOD==2021]
    df.replace({"INDICATOR": INDICATOR_dict}, inplace=True)
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

def get_indicators(df):
    indicator_list = df["INDICATOR"].unique()
    return indicator_list

def app():
    # st.title("Unaccompanied Minor Research")
    st.write(
        """
        ### Exploratory Data Analysis
          
        """
    )

    # manually setting these for now
    frequency = "annual"
    scale = "countries"
    # Associate these group labels with thier file prefixes:
    indicator_group_dict = {
            "Demographic": "DM_",
            "Economic": "ECON_",
            "Migratory": "MG_",
            "Maternal, Newborn, and Child Health": "MNCH_",
            "Post-Trauma": "PT_",
            "Water Services": "WS_"
    }

    # Lets fix how we're getting this data. We change to getttiign by group to make the UI more understandable.
    df = get_indicator_data(data_links["indicator"]["_ALL_"])

    # years_list = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
    # indicator_df = df.copy()

    row1_col1, row1_col2  = st.columns([4, 4])


    with row1_col1:
        # indicator_group = st.selectbox("**Risk Factor Group**", ["DM_", "ECON_", "MG_", "MNCH_", "PT_", "WS_"])
        indicator_group_selected = st.selectbox("**Indictator Group**", ["Demographic", "Economic", "Migratory", "Maternal, Newborn, and Child Health", "Post-Trauma", "Water Services"])
        indicator_group = indicator_group_dict[indicator_group_selected]
        
    # Get Indicator Group data
    indicator_df = get_indicator_data(data_links["indicator"][indicator_group])
    indicator_df = indicator_df[indicator_df.INDICATOR!="Net migration rate (per 1,000 population)"]
    # this_df = this_df[this_df.TIME_PERIOD==selected_year]

    with row1_col2:
        # selected_col = "OBS_VALUE" #st.selectbox("Attribute", data_cols, 4)
        # st.write(indicator_df.head(3))

        this_ind_list = indicator_df["INDICATOR"].unique().tolist()
        this_indicator = st.selectbox(f"**{indicator_group_selected} Indicators**", this_ind_list)
        # this_indicator_text = get_indicator_dict(this_indicator)

        # Display the indicator full text
        # st.write(this_indicator_text)


    # with row1_col1:
    #     # selected_col = "OBS_VALUE" #st.selectbox("Attribute", data_cols, 4)
    #     # st.write(indicator_df.head(3))
    #     this_ind_list = get_indicators(this_df)
    #     # st.write(type(this_ind_list))
    #     # this_ind_list = this_ind_list.sort()
    #     this_indicator = st.selectbox("**Indicator:**", sorted(this_ind_list))
    #     this_indicator_text = get_indicator_dict(this_indicator)
    #     # Display the indicator full text
    #     st.write(f"**{this_indicator_text}**")
    #     # st.write(f"Data type: `{this_df.OBS_VALUE.dtype}`")

    # with row1_col2:
    #     st.write(".")


    ############################################################### Trim the fat 
    net_mg_rate = df[df.INDICATOR=='Net migration rate (per 1,000 population)'].sort_values('OBS_VALUE').copy()

    def trim_the_fat(df, num):
        upp = df.sort_values('OBS_VALUE').head(num)
        lwr = df.sort_values('OBS_VALUE').tail(num)
        out = pd.concat([upp,lwr])
        return out.sort_values('REF_AREA', ascending=False)

    # Trim extremes (top-5 and bottom-5) into a new dataframe.
    top_40_nmr = trim_the_fat(net_mg_rate, 5)
    top_40_nmr.sort_values(by=["REF_AREA", "OBS_VALUE"], inplace=True)
    top_40_nmr_countries = top_40_nmr["REF_AREA"].unique()
    top_40_others = indicator_df[indicator_df["REF_AREA"].isin(top_40_nmr_countries)]               
    top_40_merged = pd.concat([top_40_nmr,top_40_others])
    top_40_merged.sort_values(by=["REF_AREA", "TIME_PERIOD", "INDICATOR"], inplace=True)
    ###############################################################
    
    # Enumerate columns
    top_40_merged.replace({"REF_AREA": REF_AREA_dict}, inplace=True)
    top_40_others.replace({"REF_AREA": REF_AREA_dict}, inplace=True)

    show_tables = "no"
    show_tables = st.checkbox("Show Dataframes")

    if show_tables:
        row1a_col1, row1a_col2 = st.columns([4, 4])

        with row1a_col1:
            st.write("**All Countries (2012 - 2022)**")
            st.write(top_40_nmr)

        with row1a_col2:
            # indicator_data_cols = get_data_columns(inventory_df, scale.lower(), frequency.lower())
            # indicator_df = indicator_df[indicator_df.INDICATOR==this_indicator]
            # st.write(f"#### {this_indicator} Layer")
            st.write("**Top-10 NMR Countries (2012 - 2022)**")
            st.write(top_40_others)


    top_40_nmr_sorted = top_40_merged.sort_values(by=["REF_AREA", "OBS_VALUE"]).copy()
    nice_plot1 = top_40_nmr_sorted[top_40_nmr_sorted.INDICATOR=="DM_NET_MG_RATE"].hvplot.box( y="OBS_VALUE", by="REF_AREA", legend=False, rot=45, width=500, height=500)
    nice_plot2 = top_40_merged[top_40_merged.INDICATOR==this_indicator].hvplot.line(
        x="REF_AREA", y="OBS_VALUE", by="TIME_PERIOD", legend_position='top_left', rot=45)
    st.write(hv.render(nice_plot2, backend='bokeh'))
    # st.write(hv.render(nice_plot2, backend='bokeh'))

    # row2_col1, row2_col2 = st.columns([4, 4])
    # with row2_col1:
    #     top_40_nmr_sorted = top_40_merged.sort_values(by=["REF_AREA", "OBS_VALUE"]).copy()
    #     nice_plot1 = top_40_nmr_sorted[top_40_nmr_sorted.INDICATOR=="DM_NET_MG_RATE"].hvplot.box( y="OBS_VALUE", by="REF_AREA", rot=55, width=900, height=500)
    #     # st.write(hv.render(nice_plot1, backend='bokeh'))

    # with row2_col2:
    #     nice_plot2 = top_40_merged[top_40_merged.INDICATOR==this_indicator].hvplot.line(x="REF_AREA", y="OBS_VALUE", by="TIME_PERIOD", rot=55, width=900, height=500)
    #     st.write(hv.render(nice_plot1*nice_plot2, backend='bokeh'))


app()
