import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from utils import initialize_session_state, format_address, format_deadline, get_address_campaigns
from components import MetaMaskConnector, Header, Footer

# Initialize session
initialize_session_state()

# Configure page
st.set_page_config(
    page_title="Dashboard - CryptoFund",
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
st.title("Dashboard")

if not st.session_state.wallet_connected:
    st.warning("Please connect your wallet to view your dashboard")
    st.stop()

# Fetch campaigns
try:
    response = requests.get("http://localhost:8000/api/campaigns")
    if response.status_code == 200:
        data = response.json()
        all_campaigns = data["campaigns"]
        
        # Filter campaigns created by the user
        user_campaigns = [c for c in all_campaigns if c["creator"].lower() == st.session_state.wallet_address.lower()]
        
        # For the demo, we'll show backed campaigns as any campaign that is not created by the user
        # In a real implementation, we would query the blockchain for contributions by this user
        backed_campaigns = []
        for campaign in all_campaigns:
            if campaign["creator"].lower() != st.session_state.wallet_address.lower():
                # Check if user has contributed to this campaign
                try:
                    contribution_response = requests.get(
                        f"http://localhost:8000/api/campaigns/{campaign['id']}/contribution/{st.session_state.wallet_address}"
                    )
                    if contribution_response.status_code == 200:
                        contribution_data = contribution_response.json()
                        if float(contribution_data["contribution"]) > 0:
                            campaign["contribution"] = contribution_data["contribution"]
                            backed_campaigns.append(campaign)
                except:
                    pass
        
        # Display tabs for different dashboard sections
        tab1, tab2, tab3 = st.tabs(["Overview", "My Campaigns", "Backed Campaigns"])
        
        with tab1:
            st.subheader("Dashboard Overview")
            
            # Account info
            st.write(f"**Account:** {format_address(st.session_state.wallet_address)}")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Campaigns Created", len(user_campaigns))
            
            with col2:
                st.metric("Campaigns Backed", len(backed_campaigns))
            
            with col3:
                # Calculate total contribution
                total_contribution = sum(float(c.get("contribution", 0)) for c in backed_campaigns)
                st.metric("Total Contributions", f"{total_contribution:.2f} ETH")
            
            # Add some visual charts if there's data
            if user_campaigns or backed_campaigns:
                st.subheader("Your Activity")
                
                # Create summary data for charts
                campaigns_df = pd.DataFrame({
                    "Type": ["Created", "Backed"],
                    "Count": [len(user_campaigns), len(backed_campaigns)]
                })
                
                # Generate a pie chart
                fig = px.pie(campaigns_df, values="Count", names="Type", 
                             title="Your Campaign Activity",
                             color_discrete_sequence=["#3498DB", "#2ECC71"])
                st.plotly_chart(fig)
            
            st.divider()
            
            # Quick actions
            st.subheader("Quick Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.button("Create New Campaign", type="primary", use_container_width=True,
                         on_click=lambda: st.switch_page("pages/create_campaign.py"))
            
            with col2:
                st.button("Explore Campaigns", use_container_width=True,
                         on_click=lambda: st.switch_page("pages/explore.py"))
        
        with tab2:
            st.subheader("My Created Campaigns")
            
            if user_campaigns:
                for campaign in user_campaigns:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.subheader(campaign["title"])
                            st.write(campaign["description"][:150] + "..." if len(campaign["description"]) > 150 else campaign["description"])
                            
                            # Progress bar
                            progress = campaign["currentAmount"] / campaign["fundingGoal"] if campaign["fundingGoal"] > 0 else 0
                            st.progress(min(progress, 1.0))
                            
                            st.write(f"💰 {campaign['currentAmount']} ETH / {campaign['fundingGoal']} ETH")
                            st.write(f"⏱️ Deadline: {format_deadline(campaign['deadline'])}")
                        
                        with col2:
                            st.button("View Details", key=f"view_{campaign['id']}", 
                                     use_container_width=True,
                                     on_click=lambda id=campaign['id']: 
                                         st.session_state.update({"campaign_id": id}) or 
                                         st.switch_page("pages/campaign_details.py"))
                            
                            # Add claimed/claim funds button based on campaign status
                            import time
                            current_time = int(time.time())
                            
                            if current_time > campaign["deadline"]:
                                if campaign["currentAmount"] >= campaign["fundingGoal"]:
                                    if campaign["claimed"]:
                                        st.success("Funds Claimed")
                                    else:
                                        st.button("Claim Funds", key=f"claim_{campaign['id']}", 
                                                 use_container_width=True, type="primary",
                                                 on_click=lambda id=campaign['id']: 
                                                     st.session_state.update({"campaign_id": id}) or 
                                                     st.switch_page("pages/campaign_details.py"))
                                else:
                                    st.error("Goal Not Reached")
                            else:
                                st.info("Campaign Active")
            else:
                st.info("You haven't created any campaigns yet")
                st.button("Create Your First Campaign", use_container_width=True,
                         on_click=lambda: st.switch_page("pages/create_campaign.py"))
        
        with tab3:
            st.subheader("Campaigns I've Backed")
            
            if backed_campaigns:
                for campaign in backed_campaigns:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.subheader(campaign["title"])
                            st.write(campaign["description"][:150] + "..." if len(campaign["description"]) > 150 else campaign["description"])
                            
                            # Progress bar
                            progress = campaign["currentAmount"] / campaign["fundingGoal"] if campaign["fundingGoal"] > 0 else 0
                            st.progress(min(progress, 1.0))
                            
                            st.write(f"💰 {campaign['currentAmount']} ETH / {campaign['fundingGoal']} ETH")
                            st.write(f"🧑‍💻 Creator: {format_address(campaign['creator'])}")
                            st.write(f"⏱️ Deadline: {format_deadline(campaign['deadline'])}")
                            
                            # Show user's contribution
                            st.write(f"**Your Contribution:** {campaign.get('contribution', 0)} ETH")
                        
                        with col2:
                            st.button("View Details", key=f"view_backed_{campaign['id']}", 
                                     use_container_width=True,
                                     on_click=lambda id=campaign['id']: 
                                         st.session_state.update({"campaign_id": id}) or 
                                         st.switch_page("pages/campaign_details.py"))
                            
                            # Show refund button if campaign failed to reach goal and is ended
                            import time
                            current_time = int(time.time())
                            
                            if current_time > campaign["deadline"] and campaign["currentAmount"] < campaign["fundingGoal"]:
                                st.button("Request Refund", key=f"refund_{campaign['id']}", 
                                         use_container_width=True, type="primary",
                                         on_click=lambda id=campaign['id']: 
                                             st.session_state.update({"campaign_id": id}) or 
                                             st.switch_page("pages/campaign_details.py"))
            else:
                st.info("You haven't backed any campaigns yet")
                st.button("Explore Campaigns to Back", use_container_width=True,
                         on_click=lambda: st.switch_page("pages/explore.py"))
                
    else:
        st.error("Failed to fetch campaigns from the API")
        
except Exception as e:
    st.error(f"Error connecting to the backend: {str(e)}")
    st.info("Make sure the backend API is running at http://localhost:8000")

# Display Footer
Footer()
