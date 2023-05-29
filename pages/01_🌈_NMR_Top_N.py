import os
import sys
# import time
# import math
# import pathlib
# import requests
# import datetime
import pandas as pd
import streamlit as st
import hvplot.pandas
# import panel as pn
import holoviews as hv
# import bokeh.plotting
import streamlit_toggle as tog

# from holoviews import opts
hv.extension('bokeh')
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
st.title("Net Migration Rate")
st.sidebar.write("""
**Sidebar**

Use the filter dropdowns to alter your results.

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
    link_prefix = "https://raw.githubusercontent.com/harry-oestreicher/umr_eda/main/data/streamlit/"
else:
    link_prefix = "data/"
    link_prefix = "data/"
    

data_links = {
    "reference": {
        "countries": link_prefix + "umr_eda_NMR.csv", # <== Net Migration
        "countries_hires": link_prefix + "umr_eda_NMR.csv", # <== Net Migration
    },
    "indicator": {
        "_ALL_": link_prefix + "all_indicators_2012-2022.csv",
        "DM_": link_prefix + "umr_data_DM_.csv",
        "ECON_": link_prefix + "umr_data_ECON_.csv",
        "ED_": link_prefix + "umr_data_ED__NEW.csv",
        "GN_": link_prefix + "umr_data_GN__NEW.csv",
        "HVA_": link_prefix + "umr_data_HVA__NEW.csv",
        "IM_": link_prefix + "umr_data_IM__NEW.csv",
        "MG_": link_prefix + "umr_data_MG_.csv",
        "MNCH_": link_prefix + "umr_data_MNCH__NEW.csv",
        "PT_": link_prefix + "umr_data_PT__NEW.csv",
        "PV_": link_prefix + "umr_data_PV_.csv",
        "WS_": link_prefix + "umr_data_WS_.csv",
        "WT_": link_prefix + "umr_data_WT__NEW.csv",
    },
}

@st.cache_data
def get_indicator_data(url):
    df = pd.read_csv(url)
    df = df[df["TIME_PERIOD"] >= 2011].copy()
    df.drop(columns=["Unnamed: 0"], inplace=True)
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

    frequency = "annual"
    scale = "countries"
    
    # Associate these group labels with file prefixes:
    indicator_group_dict = {
            "Demographic": "DM_",
            "Economic": "ECON_",
            "Migratory": "MG_",
            "Water Services": "WS_",
            "Maternal, Newborn, and Child Health": "MNCH_",
            "PT_": "PT_",
            "Youth Workforce": "WT_",
            "ED_": "ED_",
            "GN_": "GN_",
            "HVA_": "HVA_",
            "IM_": "IM_",
    }

    row0_col0, row0_col1, row0_col2  = st.columns([2,1,4])

    with row0_col0:
        num_extremes = st.slider("Number of Extreme (Hi/Low) NMR Countries to include in analysis:", min_value=2, max_value=40, value=10)

    with row0_col1:
        all_year_toggle = tog.st_toggle_switch(label="Show All NMR Years?", 
                    key='all_years', 
                    default_value=False, 
                    label_after = True, 
                    inactive_color = '#D3D3D3', 
                    active_color="#11567f", 
                    track_color="#29B5E8"
                    )
   
    with row0_col2:
        yrs = range(2012,2022+1)
        if all_year_toggle != True:
            year_selected =  st.selectbox("**Select NMR year:**", yrs)
        else:
            year_selected =  st.selectbox("**Select NMR year:**", yrs, disabled=True)

    st.write("---")

    df = get_indicator_data(data_links["indicator"]["_ALL_"])
    row1_col1, row1_col2, = st.columns([4, 4])

    with row1_col1:
        indicator_group_selected = st.selectbox("**Indictator Group:**", ["Demographic", "Economic", "Migratory", "Maternal, Newborn, and Child Health",
                                                                          "Water Services", "PT_", "Youth Workforce","ED_", "GN_", "HVA_", "IM_" ])
        indicator_group = indicator_group_dict[indicator_group_selected]      
  
    indicator_df = get_indicator_data(data_links["indicator"][indicator_group])
    indicator_df = indicator_df[indicator_df.INDICATOR!="Net migration rate (per 1,000 population)"]

    with row1_col2:
        this_ind_list = indicator_df["INDICATOR"].unique().tolist()
        this_indicator = st.selectbox(f"**{indicator_group_selected}** Indicators:", this_ind_list)

    # Remove non-numeric values for this vizualization
    if indicator_df.OBS_VALUE.dtypes == object:
        indicator_df = indicator_df[indicator_df["OBS_VALUE"].str.contains("<|>|_| |Yes|yes|No|no|Very|High|high|Medium|medium|Low|low") == False].copy()
    
    indicator_df["OBS_VALUE"] = indicator_df["OBS_VALUE"].astype(float)
    # st.write(indicator_df.OBS_VALUE.dtypes)
    net_mg_rate = df[df.INDICATOR=='Net migration rate (per 1,000 population)'].sort_values('OBS_VALUE').copy()

    if all_year_toggle != True:
        net_mg_rate = net_mg_rate[net_mg_rate.TIME_PERIOD==year_selected].copy()

    def trim_the_fat(df, num):
        upp = df.sort_values('OBS_VALUE').head(num)
        lwr = df.sort_values('OBS_VALUE').tail(num)
        out = pd.concat([upp,lwr])
        return out.sort_values('REF_AREA', ascending=False)

    # Trim extremes (top-5 and bottom-5) into a new dataframe.
    top_40_nmr = trim_the_fat(net_mg_rate, num_extremes)
    top_40_nmr.sort_values(by=["REF_AREA", "OBS_VALUE"], inplace=True)
    top_40_nmr_countries = top_40_nmr["REF_AREA"].unique()
    top_40_others = indicator_df[indicator_df["REF_AREA"].isin(top_40_nmr_countries)]

    top_40_merged = pd.concat([top_40_nmr,top_40_others])
    top_40_merged.sort_values(by=["REF_AREA", "TIME_PERIOD", "INDICATOR"], inplace=True)
    
    # Enumerate REF_AREA in all of teh dataframes
    net_mg_rate = net_mg_rate.replace({"REF_AREA": REF_AREA_dict}).copy()
    top_40_nmr = top_40_nmr.replace({"REF_AREA": REF_AREA_dict}).copy()
    top_40_merged = top_40_merged.replace({"REF_AREA": REF_AREA_dict}).copy()
    top_40_others = top_40_others.replace({"REF_AREA": REF_AREA_dict}).copy()

    show_tables = "no"
    show_tables = st.checkbox("Show Dataframes")

    if show_tables:
        row1a_col1, row1a_col2 = st.columns([4, 4])

        with row1a_col1:
            st.write("**Top-10 NMR (2012 - 2022)**")
            st.write(top_40_nmr)

        with row1a_col2:
            st.write("**Top-10 NMR All Indicators (2012 - 2022)**")
            st.write(top_40_others)


    top_40_nmr_sorted = top_40_merged.sort_values(by=["REF_AREA", "OBS_VALUE"]).copy()

    # top_40_nmr_sorted.rename(columns={"REF_AREA":"Country"}, inplace=True)
    # top_40_merged.rename(columns={"REF_AREA":"Country"}, inplace=True)

    # "Net migration rate (per 1,000 population)" | "DM_NET_MG_RATE"
    # nice_plot1 = top_40_nmr_sorted[top_40_nmr_sorted.INDICATOR=="Net migration rate (per 1,000 population)"].hvplot.line( y="OBS_VALUE", x="REF_AREA", legend=False, rot=45, width=1000, height=500)
    # nice_plot2 = top_40_merged[top_40_merged.INDICATOR==this_indicator].hvplot.scatter(y="OBS_VALUE", x="REF_AREA", by="TIME_PERIOD", rot=45, width=1000, height=500, yformatter=num_formatter, ylabel="Observation Value", xlabel="Top-N Countries", title=this_indicator )
    # st.write("### Top NMR Countries Indicator Comparison")

    nice_plot1 = top_40_nmr_sorted.hvplot()

    st.write(hv.render(nice_plot1, backend='bokeh'))

app()
