# Unaccompanied Minor Research

## Background

## Overview 

This MVP is a proof-of-concept to explore the viability of Blockchains to store immutable data for tokenized assets. A Smart Contract using ERC721 is used to collect parameters from our application and write to blockchain.

To ecconomize gas usage, we've integrated a free IPFS service to store tokenized information for each asset 'donated' through our app. This could be greatly improved by hosting an IPFS node and it's infrastructure. This is most often done using cloud services like AWS GPC or Azure to host an ethereum node.

For this app, we use Ganache to simulate the Smart Contract deployment, the mining, and the transaction storage. We've used the Pinata public IPFS cloud to store _some_ donated asset metadata and the tokenized image. To modify the _allowed_ amount of storage would have been out of scope for this project, so we store most metadata in Ganache.  In a production scenario, all metadata is tokenized and stored on a public IPFS chain.

## Getting Started & Running the Code

#### Technology Stack:

- [Streamlit](https://streamlit.io/) - User interface
- [Python](https://www.python.org/) - We use [Anaconda]() to manage Python environment.
- [Ganache](https://trufflesuite.com/ganache/) - Local blochain for dev/testing
- [Web3.py](https://web3py.readthedocs.io/en/stable/) - Smart Contract interaction
- [Remix - remix.ethereum.org](https://remix.ethereum.org/)
- [Pinata](https://gateway.pinana.cloud) or other IPFS host provider (API Key and Secret API Key)
- [MetaMask](https://metamask.io/) - Installed into your chrome or edge browser. We will create dummy accounts to run the app.


## 1. Setup Environment

