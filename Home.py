# -*- coding: utf-8 -*-
import os
import logging
import streamlit as st
import sys
import time
# import streamlit.components.v1 as components
import src.utils.streamlit_gui as utl
from pathlib import Path
from PIL import Image

# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'

st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state, layout="wide")
st.sidebar.markdown('Several open-source packages are used to process the data and generate the visualizations, e.g., streamlit, geopandas, leafmap, and pydeck.')

def main():

    utl.set_page_title('UMR Exploratory Data Analysis')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    utl.local_css("src/css/streamlit.css")
    utl.remote_css("https://fonts.googleapis.com/icon?family=Material+Icons")

    # Page Header information
    st.title("Unaccompanied Minor Research", anchor=None)
    st.write("### Exploratory Data Analysis")
    st.write("""Welcome. This vizualization tool allows you to explore associated risk factors with Net Migraion Rate of unaccompanied minors.""")
    st.markdown("---")
    return

if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    # df = load_data()
    main()
