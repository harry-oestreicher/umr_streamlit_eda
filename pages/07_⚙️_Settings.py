# -*- coding: utf-8 -*-
import logging, os
import streamlit as st
from src.utils.dataio import get_data, init_data
import streamlit.components.v1 as components
from dotenv import load_dotenv
from web3 import Web3

# Load the required variables from .env file
load_dotenv()

contract_address = os.getenv("SMART_CONTRACT_ADDRESS")
contract_abi = os.getenv("ABI_PATH")
ipfs_uri = os.getenv("IPFS_URI")
# recipient_df = get_data("SELECT Organization, City, Address from ORGANIZATIONS")
# categories_df = get_data("SELECT DISTINCT Category from ASSETS")
# resources_df = get_data("SELECT Category, Item, QtySize, USD, Tags from ASSETS")
donor_account = os.getenv("PUBLIC_KEY")
web3_provider_uri = os.getenv("WEB3_PROVIDER_URI")

# Instantiate a web3 object inline
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))


# Begin Streamlit calls
st.set_page_config(layout="wide")

def main():
    #Header information 
    st.title("System Settings and Data", anchor=None)
    # st.markdown("Web3 settings:")
    # st.markdown("---")
    # st.write(donor_account)
    # st.write(contract_address)
    # st.write(contract_abi)
    # st.write(ipfs_uri)
    # st.write(web3_provider_uri)
    # st.markdown("---")

    btn =  st.button("Initialize and seed the database")
    if btn:
        # re-initialize the database
        init_data()
        # Display the tables
        org_query="SELECT * FROM ORGANIZATIONS;"
        org_df = get_data(org_query)
        assets_query="SELECT * FROM ASSETS;"
        assets_df = get_data(assets_query)
        transactions_query="SELECT * FROM TRANSACTIONS;"
        transactions_df = get_data(transactions_query)
        cities_query="SELECT * FROM CITIES;"
        cities_df = get_data(cities_query)
        st.write("ORGANIZATION")
        st.dataframe(org_df)
        st.write("---")
        st.write("TRANSACTIONS")
        st.dataframe(transactions_df)
        st.write("---")
        st.write("ASSETS")
        st.dataframe(assets_df)
        st.write("---")
        st.write("CITIES")
        st.dataframe(cities_df)

if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    main()
