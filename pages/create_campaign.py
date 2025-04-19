import streamlit as st
import requests
import json
import datetime
from utils import initialize_session_state
from components import MetaMaskConnector, Header, Footer

# Initialize session
initialize_session_state()

# Configure page
st.set_page_config(
    page_title="Create Campaign - CryptoFund",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display Header
Header()

# MetaMask Connection
wallet_connector = MetaMaskConnector()
wallet_connector.render()

# Main Content
st.title("Create a New Campaign")

if not st.session_state.wallet_connected:
    st.warning("Please connect your wallet to create a campaign")
else:
    # Campaign creation form
    with st.form("campaign_form"):
        st.subheader("Campaign Details")
        
        title = st.text_input("Campaign Title", max_chars=100)
        description = st.text_area("Campaign Description", max_chars=2000)
        image_url = st.text_input("Campaign Image URL", 
                                  placeholder="https://example.com/image.jpg")
        
        col1, col2 = st.columns(2)
        
        with col1:
            funding_goal = st.number_input("Funding Goal (ETH)", 
                                         min_value=0.01, 
                                         max_value=1000.0, 
                                         value=1.0, 
                                         step=0.1)
        
        with col2:
            duration = st.slider("Campaign Duration (days)", 
                               min_value=1, 
                               max_value=90, 
                               value=30)
        
        st.markdown("**Important Notes:**")
        st.markdown("- Your campaign will be deployed on the Sepolia testnet")
        st.markdown("- You'll need to pay a small gas fee to create the campaign")
        st.markdown("- All transactions are transparent and publicly visible on the blockchain")
        
        submit_button = st.form_submit_button("Create Campaign", use_container_width=True)
        
        if submit_button:
            if not title or not description or not image_url:
                st.error("Please fill in all required fields")
            else:
                # In a real implementation, this would interact with Web3.js to create the transaction
                # For now, we'll just display what would happen
                try:
                    # Get contract information
                    contract_response = requests.get("http://localhost:8000/api/contract")
                    if contract_response.status_code == 200:
                        contract_data = contract_response.json()
                        
                        # Display transaction information
                        st.success("Campaign ready for submission")
                        
                        st.write("#### Transaction Preview")
                        st.json({
                            "contract": contract_data["address"],
                            "method": "createCampaign",
                            "parameters": {
                                "title": title,
                                "description": description,
                                "imageUrl": image_url,
                                "fundingGoal": funding_goal,
                                "durationInDays": duration
                            },
                            "from": st.session_state.wallet_address
                        })
                        
                        # Display the code to execute from browser console
                        st.write("#### Execute this transaction in your browser console")
                        
                        js_code = f"""
                        const web3 = new Web3(window.ethereum);
                        
                        const contractAddress = "{contract_data["address"]}";
                        const contractABI = {json.dumps(contract_data["abi"])};
                        
                        const contract = new web3.eth.Contract(contractABI, contractAddress);
                        
                        async function createCampaign() {{
                            try {{
                                const accounts = await ethereum.request({{ method: 'eth_requestAccounts' }});
                                const account = accounts[0];
                                
                                const fundingGoalWei = web3.utils.toWei("{funding_goal}", "ether");
                                
                                const result = await contract.methods.createCampaign(
                                    "{title}",
                                    "{description}",
                                    "{image_url}",
                                    fundingGoalWei,
                                    {duration}
                                ).send({{ from: account }});
                                
                                console.log("Transaction successful:", result);
                                alert("Campaign created successfully! Transaction hash: " + result.transactionHash);
                            }} catch (error) {{
                                console.error("Error creating campaign:", error);
                                alert("Failed to create campaign: " + error.message);
                            }}
                        }}
                        
                        createCampaign();
                        """
                        
                        st.code(js_code, language="javascript")
                        
                        # Add JavaScript executor
                        st.components.v1.html(f"""
                        <button onclick="executeTransaction()" style="background-color: #3498DB; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">
                            Submit Transaction
                        </button>
                        
                        <script src="https://cdn.jsdelivr.net/npm/web3@latest/dist/web3.min.js"></script>
                        <script>
                        async function executeTransaction() {{
                            if (typeof window.ethereum !== 'undefined') {{
                                const web3 = new Web3(window.ethereum);
                                
                                const contractAddress = "{contract_data["address"]}";
                                const contractABI = {json.dumps(contract_data["abi"])};
                                
                                const contract = new web3.eth.Contract(contractABI, contractAddress);
                                
                                try {{
                                    const accounts = await ethereum.request({{ method: 'eth_requestAccounts' }});
                                    const account = accounts[0];
                                    
                                    const fundingGoalWei = web3.utils.toWei("{funding_goal}", "ether");
                                    
                                    const result = await contract.methods.createCampaign(
                                        "{title}",
                                        "{description}",
                                        "{image_url}",
                                        fundingGoalWei,
                                        {duration}
                                    ).send({{ from: account }});
                                    
                                    console.log("Transaction successful:", result);
                                    alert("Campaign created successfully! Transaction hash: " + result.transactionHash);
                                    
                                    // Redirect to home page
                                    window.location.href = "/";
                                }} catch (error) {{
                                    console.error("Error creating campaign:", error);
                                    alert("Failed to create campaign: " + error.message);
                                }}
                            }} else {{
                                alert("MetaMask is not installed. Please install MetaMask to use this application.");
                            }}
                        }}
                        </script>
                        """, height=60)
                        
                    else:
                        st.error("Failed to get contract information from the API")
                except Exception as e:
                    st.error(f"Error connecting to the backend: {str(e)}")
                    st.info("Make sure the backend API is running at http://localhost:8000")

# Display Footer
Footer()
