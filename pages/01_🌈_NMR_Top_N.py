import os
import sys
import pandas as pd
import streamlit as st
import bokeh.plotting
from bokeh.plotting import figure

sys.path.append("..")
from data.dictionary import get_dictionary
INDICATOR_dict = get_dictionary('INDICATOR')
REF_AREA_dict = get_dictionary('REF_AREA')

# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

# Streamlit set_page_config method has a 'initial_sidebar_state' argument that controls sidebar state.
st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state, layout="wide")

st.title("Net Migration Rate")
st.sidebar.write("""
**Sidebar**

Use the filter dropdowns to alter your results.

Use the checkbox to preview dataframes while rendering visualzations.

""")

with st.sidebar:
    fetch_from_cloud = st.radio(
    "Fetch data from github?",
    ('No', 'Yes'))

if fetch_from_cloud == 'Yes':
    link_prefix = "https://raw.githubusercontent.com/harry-oestreicher/umr_eda/main/data/streamlit/"
else:
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
        "MG_": link_prefix + "umr_data_MG_.csv",
        "PV_": link_prefix + "umr_data_PV_.csv",
        "WS_": link_prefix + "umr_data_WS_.csv",
        "WT_": link_prefix + "umr_data_WT_.csv",
        "ED_": link_prefix + "umr_data_ED_.csv",
        "GN_": link_prefix + "umr_data_GN_.csv",
        "HVA_": link_prefix + "umr_data_HVA_.csv",
        "IM_": link_prefix + "umr_data_IM_.csv",
        "MNCH_": link_prefix + "umr_data_MNCH_.csv",
        "PT_": link_prefix + "umr_data_PT_.csv",
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
        Exploratory Data Analysis tool for net migration rate and environmental indicators datasets.
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
            "Youth Workforce": "WT_",
            "Education": "ED_",
            "PT_": "PT_",
            "GN_": "GN_",
            "HVA_": "HVA_",
            "IM_": "IM_",
    }

    st.write("#### Net Migration Rate Filters:")
    row0_col0, row0_col1, row0_col2  = st.columns([2,1,4])
    with row0_col0:
        num_extremes = st.slider("Number of Extreme (Hi/Low) NMR Countries to include in analysis:", min_value=2, max_value=40, value=10)

    with row0_col1:
        all_year_toggle = st.radio(
            "Combine all  NMR years?",
            ('Yes', 'No'))
   
    with row0_col2:
        yrs = range(2012,2022+1)
        if all_year_toggle == 'No':
            year_selected =  st.selectbox("**Select NMR year:**", yrs)
        else:
            year_selected =  st.selectbox("**Select NMR year:**", yrs, disabled=True)

    st.write(" ")

    df = get_indicator_data(data_links["indicator"]["_ALL_"])
    net_mg_rate = df[df.INDICATOR=='Net migration rate (per 1,000 population)'].sort_values('OBS_VALUE').copy()

    if all_year_toggle == 'No':
        net_mg_rate = net_mg_rate[net_mg_rate.TIME_PERIOD==year_selected].copy()

    def trim_the_fat(df, num):
        upp = df.sort_values('OBS_VALUE').head(num)
        lwr = df.sort_values('OBS_VALUE').tail(num)
        out = pd.concat([upp,lwr])
        return out.sort_values('REF_AREA', ascending=False)

    # Trim extremes (topN and bottomN) into a new dataframe.
    top_40_nmr = trim_the_fat(net_mg_rate, num_extremes)
    top_40_nmr.sort_values(by=["REF_AREA", "OBS_VALUE"], inplace=True)
    top_40_nmr_countries = top_40_nmr["REF_AREA"].unique()

    st.write("#### Indicator Groups and Filters:")
    row1_col1, row1_col2, = st.columns([4, 4])
    with row1_col1:
        indicator_group_selected = st.selectbox("**Indictator Group:**", [
            "Demographic", 
            "Economic", 
            "Migratory", 
            "Maternal, Newborn, and Child Health",
            "Water Services", 
            "Youth Workforce",
            "Education", 
            "PT_",
            "GN_", 
            "HVA_", 
            "IM_"
            ]
        )
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

    top_40_others = indicator_df[indicator_df["REF_AREA"].isin(top_40_nmr_countries)]

    top_40_merged = pd.concat([top_40_nmr,top_40_others])
    top_40_merged.sort_values(by=["REF_AREA", "TIME_PERIOD", "INDICATOR"], inplace=True)
    
    # Enumerate REF_AREA
    net_mg_rate = net_mg_rate.replace({"REF_AREA": REF_AREA_dict}).copy()
    top_40_nmr = top_40_nmr.replace({"REF_AREA": REF_AREA_dict}).copy()
    top_40_merged = top_40_merged.replace({"REF_AREA": REF_AREA_dict}).copy()
    top_40_others = top_40_others.replace({"REF_AREA": REF_AREA_dict}).copy()

    top_40_nmr_sorted = top_40_merged.sort_values(by=["REF_AREA", "OBS_VALUE"]).copy()
    nmr_df = top_40_nmr_sorted[top_40_nmr_sorted.INDICATOR=="Net migration rate (per 1,000 population)"].copy()
    ind_df = top_40_merged[top_40_merged.INDICATOR==this_indicator].copy()

    merged_df = nmr_df.merge(ind_df, on=["REF_AREA", "TIME_PERIOD"], how='inner').copy()
    merged_df.rename(columns={"REF_AREA": "Country", "OBS_VALUE_x": "Net Migration Rate", "OBS_VALUE_y": this_indicator}, inplace=True)

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

        st.write("**Merged Tables**")
        st.dataframe(merged_df)

    st.line_chart(merged_df, y=['Net Migration Rate', this_indicator], x='Country', height=500)

app()
