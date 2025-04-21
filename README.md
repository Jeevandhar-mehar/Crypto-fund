# Decentralized Fund Raiser

## Overview
The Decentralized Fund Raiser project is a blockchain-based platform that allows users to create and manage fundraising campaigns in a decentralized manner. It leverages smart contracts to ensure transparency, immutability, and trust in the fundraising process.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Setup Guide](#setup-guide)
  - [Prerequisites](#prerequisites)Create a README.md file from the above provided steps and make sure that it has sections like Title, Overview, Table of contents, Features, sub-title for each step in the workflow of the project.
  - [Installation](#installation)
  - [Environment Setup](#environment-setup)
  - [Running the Project](#running-the-project)
- [Significance](#significance)

## Features
- Decentralized platform for fundraising campaigns.
- Transparent and immutable transactions using blockchain.
- Smart contract integration for secure fund management.
- User-friendly interface for creating and managing campaigns.Create a README.md file from the above provided steps and make sure that it has sections like Title, Overview, Table of contents, Features, sub-title for each step in the workflow of the project.

## Setup GuideCreate a README.md file from the above provided steps and make sure that it has sections like Title, Overview, Table of contents, Features, sub-title for each step in the workflow of the project.

### Prerequisites
Before setting up the project, ensure you have the following installed:
- Node.js (v14 or higher)
- npm or yarn
- Truffle or Hardhat (for smart contract development)
- Ganache (or any Ethereum-compatible local blockchain)
- MetaMask (browser extension for interacting with the blockchain)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/DecentralizedFundRaiser.git
   cd DecentralizedFundRaiser
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Environment Setup
1. Create a `.env` file in the root directory and configure the following variables:
   ```
   INFURA_API_KEY=<your-infura-api-key>
   PRIVATE_KEY=<your-wallet-private-key>
   NETWORK=<network-name>
   ```

2. Ensure your MetaMask wallet is connected to the same network as specified in the `.env` file.

### Running the Project
1. Compile the smart contracts:
   ```bash
   npx hardhat compile
   ```

2. Deploy the smart contracts:
   ```bash
   npx hardhat run scripts/deploy.js --network <network-name>
   ```

3. Start the frontend application:
   ```bash
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000` to interact with the application.

## Significance
The Decentralized Fund Raiser project addresses the challenges of trust and transparency in traditional fundraising platforms. By leveraging blockchain technology, it ensures that funds are securely managed and transactions are immutable. This project empowers users to create campaigns with confidence and provides donors with assurance that their contributions are used as intended.

