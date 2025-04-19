import streamlit as st
import requests
import json
from utils import initialize_session_state, format_address, format_deadline
from components import MetaMaskConnector, Header, Footer

# Initialize session
initialize_session_state()

# Configure page
st.set_page_config(
    page_title="CryptoFund - Decentralized Crowdfunding",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display Header
Header()

# Main Content
st.title("🌱 CryptoFund")
st.subheader("Decentralized Crowdfunding on Ethereum")

# MetaMask Connection
wallet_connector = MetaMaskConnector()
wallet_connector.render()

if st.session_state.wallet_connected:
    # Fetch some recent campaigns to display on the home page
    try:
        # Use the development mode API to fetch some sample campaigns
        response = requests.get("http://localhost:8000/api/campaigns")
        if response.status_code == 200:
            data = response.json()
            recent_campaigns = data["campaigns"][-3:] if len(data["campaigns"]) > 3 else data["campaigns"]
            
            # Fetch additional metadata for each campaign
            for campaign in recent_campaigns:
                try:
                    metadata_response = requests.get(f"http://localhost:8000/api/campaign-metadata/{campaign['id']}")
                    if metadata_response.status_code == 200:
                        metadata = metadata_response.json()["campaign"]
                        # Enhance campaign with metadata
                        campaign["title"] = metadata.get("title", f"Campaign {campaign['id']}")
                        campaign["description"] = metadata.get("description", "No description available")
                        campaign["image_url"] = metadata.get("image_url", "")
                except Exception as e:
                    print(f"Error fetching campaign metadata: {e}")
            
            if recent_campaigns:
                st.subheader("Recent Campaigns")
                
                col1, col2, col3 = st.columns(3)
                
                for i, campaign in enumerate(recent_campaigns):
                    col = [col1, col2, col3][i % 3]
                    with col:
                        with st.container(border=True):
                            st.subheader(campaign["title"])
                            st.write(campaign["description"][:100] + "..." if len(campaign["description"]) > 100 else campaign["description"])
                            
                            # Progress bar
                            progress = campaign["currentAmount"] / campaign["fundingGoal"] if campaign["fundingGoal"] > 0 else 0
                            st.progress(min(progress, 1.0))
                            
                            st.write(f"💰 {campaign['currentAmount']} ETH / {campaign['fundingGoal']} ETH")
                            st.write(f"🧑‍💻 Creator: {format_address(campaign['creator'])}")
                            st.write(f"⏱️ Deadline: {format_deadline(campaign['deadline'])}")
                            
                            st.button("View Details", key=f"view_{campaign['id']}", 
                                      on_click=lambda id=campaign['id']: st.session_state.update({"page": "campaign_details", "campaign_id": id}))
            
            st.markdown("### Explore more campaigns and create your own!")
            col1, col2 = st.columns(2)
            
            with col1:
                st.button("Explore All Campaigns", use_container_width=True, on_click=lambda: st.switch_page("pages/explore.py"))
            
            with col2:
                st.button("Create a Campaign", use_container_width=True, on_click=lambda: st.switch_page("pages/create_campaign.py"))
                
        else:
            st.error("Failed to fetch campaigns from the API")
            
    except Exception as e:
        st.error(f"Error connecting to the backend: {str(e)}")
        st.info("Make sure the backend API is running at http://localhost:8000")
else:
    # Introduction for users who haven't connected their wallet
    st.info("👆 Connect your MetaMask wallet to get started")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### What is CryptoFund?
        
        CryptoFund is a decentralized crowdfunding platform built on Ethereum that allows creators to raise funds for their projects and ideas.
        
        **Key Features:**
        - Create your own fundraising campaigns
        - Contribute to campaigns with Ethereum
        - Transparent and secure fund management through smart contracts
        - No intermediaries or platform fees
        """)
    
    with col2:
        st.markdown("""
        ### How it works
        
        1. **Connect your wallet** - Use MetaMask to interact with the Ethereum blockchain
        2. **Create a campaign** - Set your funding goal, deadline, and campaign details
        3. **Share and receive funding** - Others can contribute ETH to your campaign
        4. **Claim funds** - If your goal is reached, you can claim the funds once the deadline passes
        
        All transactions happen on the Sepolia testnet, so you can try it out without using real ETH.
        """)

# Display Footer
Footer()
