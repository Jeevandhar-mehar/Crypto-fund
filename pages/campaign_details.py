import streamlit as st
import requests
import json
from utils import initialize_session_state, format_address, format_deadline, calculate_time_left, format_timestamp
from components import MetaMaskConnector, Header, Footer

# Initialize session
initialize_session_state()

# Configure page
st.set_page_config(
    page_title="Campaign Details - CryptoFund",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display Header
Header()

# MetaMask Connection
wallet_connector = MetaMaskConnector()
wallet_connector.render()

# Get campaign ID from URL parameter or session state
if "campaign_id" in st.query_params:
    campaign_id = st.query_params["campaign_id"][0]
    st.session_state.campaign_id = campaign_id
elif "campaign_id" in st.session_state:
    campaign_id = st.session_state.campaign_id
else:
    st.error("No campaign specified")
    st.button("Go to Explore", on_click=lambda: st.switch_page("pages/explore.py"))
    st.stop()

# Fetch campaign details
try:
    response = requests.get(f"http://localhost:8000/api/campaigns/{campaign_id}")
    if response.status_code == 200:
        data = response.json()
        campaign = data["campaign"]
        
        # Main content
        st.title(campaign["title"])
        
        # Campaign info
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(campaign["imageUrl"], use_column_width=True)
            
            st.subheader("Campaign Description")
            st.write(campaign["description"])
            
            # If user is the creator, show creator controls
            if st.session_state.wallet_connected and st.session_state.wallet_address.lower() == campaign["creator"].lower():
                st.divider()
                st.subheader("Creator Controls")
                
                import time
                current_time = int(time.time())
                
                if current_time > campaign["deadline"]:
                    if campaign["currentAmount"] >= campaign["fundingGoal"]:
                        if not campaign["claimed"]:
                            st.success("Your campaign has been successfully funded! You can now claim the funds.")
                            
                            # Claim funds button
                            st.button("Claim Funds", type="primary", use_container_width=True, 
                                     key="claim_funds_button")
                            
                            # Add JavaScript for claiming funds
                            if "contract_address" not in st.session_state or not st.session_state.contract_address:
                                # Get contract information
                                contract_response = requests.get("http://localhost:8000/api/contract")
                                if contract_response.status_code == 200:
                                    contract_data = contract_response.json()
                                    st.session_state.contract_address = contract_data["address"]
                                    st.session_state.contract_abi = contract_data["abi"]
                            
                            st.components.v1.html(f"""
                            <script src="https://cdn.jsdelivr.net/npm/web3@latest/dist/web3.min.js"></script>
                            <script>
                            async function claimFunds() {{
                                if (typeof window.ethereum !== 'undefined') {{
                                    const web3 = new Web3(window.ethereum);
                                    
                                    const contractAddress = "{st.session_state.contract_address}";
                                    const contractABI = {json.dumps(st.session_state.contract_abi)};
                                    
                                    const contract = new web3.eth.Contract(contractABI, contractAddress);
                                    
                                    try {{
                                        const accounts = await ethereum.request({{ method: 'eth_requestAccounts' }});
                                        const account = accounts[0];
                                        
                                        const result = await contract.methods.claimFunds({campaign_id}).send({{ from: account }});
                                        
                                        console.log("Transaction successful:", result);
                                        alert("Funds claimed successfully! Transaction hash: " + result.transactionHash);
                                        
                                        // Refresh page
                                        window.location.reload();
                                    }} catch (error) {{
                                        console.error("Error claiming funds:", error);
                                        alert("Failed to claim funds: " + error.message);
                                    }}
                                }}
                            }}
                            
                            // Set up listener for the claim funds button
                            const streamlitDoc = window.parent.document;
                            const buttons = streamlitDoc.querySelectorAll('button');
                            for (const button of buttons) {{
                                if (button.innerText === 'Claim Funds') {{
                                    button.addEventListener('click', claimFunds);
                                }}
                            }}
                            </script>
                            """, height=0)
                        else:
                            st.success("You have already claimed the funds for this campaign.")
                    else:
                        st.error("Your campaign did not reach its funding goal by the deadline.")
                else:
                    st.info(f"Your campaign is still active. You can claim funds after the deadline ({format_deadline(campaign['deadline'])}).")
        
        with col2:
            with st.container(border=True):
                st.subheader("Campaign Details")
                
                # Progress bar
                progress = campaign["currentAmount"] / campaign["fundingGoal"] if campaign["fundingGoal"] > 0 else 0
                st.progress(min(progress, 1.0))
                
                st.metric("Funding Progress", f"{campaign['currentAmount']} ETH", f"{progress:.1%}")
                
                st.write(f"**Funding Goal:** {campaign['fundingGoal']} ETH")
                
                # Time remaining
                time_left = calculate_time_left(campaign["deadline"])
                st.write(f"**Time Remaining:** {time_left}")
                st.write(f"**Deadline:** {format_timestamp(campaign['deadline'])}")
                
                st.write(f"**Creator:** {format_address(campaign['creator'])}")
                
                # Contribution form
                if st.session_state.wallet_connected:
                    import time
                    current_time = int(time.time())
                    
                    if current_time < campaign["deadline"]:
                        st.divider()
                        st.subheader("Contribute to this Campaign")
                        
                        contribution_amount = st.number_input("Amount (ETH)", 
                                                           min_value=0.01, 
                                                           max_value=float(campaign["fundingGoal"]) * 2, 
                                                           value=0.1, 
                                                           step=0.01)
                        
                        contribute_button = st.button("Contribute", type="primary", use_container_width=True)
                        
                        # Add JavaScript for contribution
                        if "contract_address" not in st.session_state or not st.session_state.contract_address:
                            # Get contract information
                            contract_response = requests.get("http://localhost:8000/api/contract")
                            if contract_response.status_code == 200:
                                contract_data = contract_response.json()
                                st.session_state.contract_address = contract_data["address"]
                                st.session_state.contract_abi = contract_data["abi"]
                        
                        st.components.v1.html(f"""
                        <script src="https://cdn.jsdelivr.net/npm/web3@latest/dist/web3.min.js"></script>
                        <script>
                        async function contribute() {{
                            if (typeof window.ethereum !== 'undefined') {{
                                const web3 = new Web3(window.ethereum);
                                
                                const contractAddress = "{st.session_state.contract_address}";
                                const contractABI = {json.dumps(st.session_state.contract_abi)};
                                
                                const contract = new web3.eth.Contract(contractABI, contractAddress);
                                
                                try {{
                                    const accounts = await ethereum.request({{ method: 'eth_requestAccounts' }});
                                    const account = accounts[0];
                                    
                                    const weiAmount = web3.utils.toWei("{contribution_amount}", "ether");
                                    
                                    const result = await contract.methods.contribute({campaign_id}).send({{ 
                                        from: account,
                                        value: weiAmount
                                    }});
                                    
                                    console.log("Transaction successful:", result);
                                    alert("Contribution successful! Transaction hash: " + result.transactionHash);
                                    
                                    // Refresh page
                                    window.location.reload();
                                }} catch (error) {{
                                    console.error("Error contributing:", error);
                                    alert("Failed to contribute: " + error.message);
                                }}
                            }}
                        }}
                        
                        // Set up listener for the contribute button
                        const streamlitDoc = window.parent.document;
                        const buttons = streamlitDoc.querySelectorAll('button');
                        for (const button of buttons) {{
                            if (button.innerText === 'Contribute') {{
                                button.addEventListener('click', contribute);
                            }}
                        }}
                        </script>
                        """, height=0)
                        
                        st.divider()
                        
                        # If user has contributed, show their contribution
                        if st.session_state.wallet_connected:
                            try:
                                contribution_response = requests.get(
                                    f"http://localhost:8000/api/campaigns/{campaign_id}/contribution/{st.session_state.wallet_address}"
                                )
                                if contribution_response.status_code == 200:
                                    contribution_data = contribution_response.json()
                                    contribution = contribution_data["contribution"]
                                    
                                    if float(contribution) > 0:
                                        st.success(f"You have contributed {contribution} ETH to this campaign")
                            except Exception as e:
                                st.error(f"Error getting contribution data: {str(e)}")
                    else:
                        if campaign["currentAmount"] < campaign["fundingGoal"]:
                            st.warning("This campaign has ended without reaching its funding goal.")
                            
                            # Check if user has contributed
                            if st.session_state.wallet_connected:
                                try:
                                    contribution_response = requests.get(
                                        f"http://localhost:8000/api/campaigns/{campaign_id}/contribution/{st.session_state.wallet_address}"
                                    )
                                    if contribution_response.status_code == 200:
                                        contribution_data = contribution_response.json()
                                        contribution = contribution_data["contribution"]
                                        
                                        if float(contribution) > 0:
                                            st.info(f"You contributed {contribution} ETH to this campaign. You can request a refund.")
                                            
                                            # Refund button
                                            st.button("Request Refund", type="primary", use_container_width=True, 
                                                    key="refund_button")
                                            
                                            # Add JavaScript for refund
                                            st.components.v1.html(f"""
                                            <script src="https://cdn.jsdelivr.net/npm/web3@latest/dist/web3.min.js"></script>
                                            <script>
                                            async function requestRefund() {{
                                                if (typeof window.ethereum !== 'undefined') {{
                                                    const web3 = new Web3(window.ethereum);
                                                    
                                                    const contractAddress = "{st.session_state.contract_address}";
                                                    const contractABI = {json.dumps(st.session_state.contract_abi)};
                                                    
                                                    const contract = new web3.eth.Contract(contractABI, contractAddress);
                                                    
                                                    try {{
                                                        const accounts = await ethereum.request({{ method: 'eth_requestAccounts' }});
                                                        const account = accounts[0];
                                                        
                                                        const result = await contract.methods.requestRefund({campaign_id}).send({{ from: account }});
                                                        
                                                        console.log("Transaction successful:", result);
                                                        alert("Refund requested successfully! Transaction hash: " + result.transactionHash);
                                                        
                                                        // Refresh page
                                                        window.location.reload();
                                                    }} catch (error) {{
                                                        console.error("Error requesting refund:", error);
                                                        alert("Failed to request refund: " + error.message);
                                                    }}
                                                }}
                                            }}
                                            
                                            // Set up listener for the refund button
                                            const streamlitDoc = window.parent.document;
                                            const buttons = streamlitDoc.querySelectorAll('button');
                                            for (const button of buttons) {{
                                                if (button.innerText === 'Request Refund') {{
                                                    button.addEventListener('click', requestRefund);
                                                }}
                                            }}
                                            </script>
                                            """, height=0)
                                except Exception as e:
                                    st.error(f"Error getting contribution data: {str(e)}")
                        else:
                            st.success("This campaign has successfully reached its funding goal!")
                else:
                    st.info("Connect your wallet to contribute to this campaign")
            
            # Campaign stats
            with st.container(border=True):
                st.subheader("Campaign Stats")
                
                # Calculate days left
                import time
                current_time = int(time.time())
                days_left = max(0, (campaign["deadline"] - current_time) // (24 * 3600))
                
                # Stats
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Days Left", f"{days_left}")
                
                with col2:
                    contributors = 0  # This would come from the blockchain in a real implementation
                    st.metric("Contributors", f"{contributors}")
    else:
        st.error(f"Failed to fetch campaign details: {response.text}")
        st.button("Go to Explore", on_click=lambda: st.switch_page("pages/explore.py"))

except Exception as e:
    st.error(f"Error connecting to the backend: {str(e)}")
    st.info("Make sure the backend API is running at http://localhost:8000")
    st.button("Go to Explore", on_click=lambda: st.switch_page("pages/explore.py"))

# Display Footer
Footer()
