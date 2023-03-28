# -*- coding: utf-8 -*-
import os
import logging
import streamlit as st

import sys
import time
from pathlib import Path

# sys.path.append("..")
import src.utils.streamlit_gui as utl
from PIL import Image

from src.utils.dataio import init_data, get_data
import streamlit.components.v1 as components
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

contract_address = os.getenv("SMART_CONTRACT_ADDRESS")
contract_abi = os.getenv("ABI_PATH")

# Begin Streamlit
# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'collapsed'

# Streamlit set_page_config method has a 'initial_sidebar_state' argument that controls sidebar state.
st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state, layout="wide")

# Show title and description of the app.
# st.title('Example: Controlling sidebar programmatically')
st.sidebar.markdown('This is an example Streamlit app to show how to expand and collapse the sidebar programmatically.')

def main(df):

    dir_root = os.path.dirname(os.path.abspath(__file__))
    utl.set_page_title('UMR Exploratory Data Analysis')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    utl.local_css("frontend/css/streamlit.css")
    utl.remote_css("https://fonts.googleapis.com/icon?family=Material+Icons")
    # logo = Image.open(f"{dir_root}/frontend/feral.jpg")

    # Page Header information
    st.title("Unaccompanied Minor Research", anchor=None)
    st.write("### Exploratory Data Analysis")
    st.write("""This MVP explores the risk factors related to underage migrant youths.""")
    # st.markdown("**Settings:**")
    # st.write(f"Contract Address: {contract_address}")
    # st.write(f"Contract ABI: {contract_abi}")
    # st.markdown("---")
    # st.image("https://www.bbva.com/wp-content/uploads/en/2017/07/blockchain-humanitario.jpg", width=600)
    return

    # ## Sidebar voodoo
    # if st.session_state.sidebar_state == 'collapsed':
    #     print(style_on)
    # else:
    #     print(style_off)

    # # Toggle sidebar state between 'expanded' and 'collapsed'.
    # if st.button('Expand Sidebar'):
    #     # CSS class css-1offfwp e16nr0p34
    #     st.session_state.sidebar_state = 'collapsed' if st.session_state.sidebar_state == 'expanded' else 'expanded'
    #     # Force an app rerun after switching the sidebar state.
    #     st.experimental_rerun()

    # st.image("https://www.bbva.com/wp-content/uploads/en/2017/07/blockchain-humanitario.jpg", width=600)

# @st.cache
def load_data():
    # This is a compulory query that is available on each page to build out the solution with additional functionality.
    query_str = "SELECT * FROM ASSETS;"
    df = get_data(query_str)
    return df

if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    df = load_data()
    main(df)