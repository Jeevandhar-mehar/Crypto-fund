import streamlit as st
import requests
from utils import initialize_session_state, format_address, format_deadline, calculate_time_left
from components import MetaMaskConnector, Header, Footer

# Initialize session
initialize_session_state()

# Configure page
st.set_page_config(
    page_title="Explore Campaigns - CryptoFund",
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
st.title("Explore Campaigns")

if not st.session_state.wallet_connected:
    st.warning("Please connect your wallet to interact with campaigns")

# Fetch campaigns
try:
    response = requests.get("http://localhost:8000/api/campaigns")
    if response.status_code == 200:
        data = response.json()
        campaigns = data["campaigns"]
        
        # Add search and filter options
        search_col, filter_col = st.columns([2, 1])
        
        with search_col:
            search_term = st.text_input("Search campaigns", placeholder="Search by title or description")
        
        with filter_col:
            filter_option = st.selectbox("Filter by", 
                                      ["All", "Active", "Completed", "Funded", "Not Funded"])
        
        # Apply filters
        filtered_campaigns = campaigns
        
        if search_term:
            filtered_campaigns = [c for c in filtered_campaigns 
                               if search_term.lower() in c["title"].lower() 
                               or search_term.lower() in c["description"].lower()]
        
        if filter_option == "Active":
            import time
            current_time = int(time.time())
            filtered_campaigns = [c for c in filtered_campaigns if c["deadline"] > current_time]
        
        elif filter_option == "Completed":
            import time
            current_time = int(time.time())
            filtered_campaigns = [c for c in filtered_campaigns if c["deadline"] <= current_time]
        
        elif filter_option == "Funded":
            filtered_campaigns = [c for c in filtered_campaigns 
                               if float(c["currentAmount"]) >= float(c["fundingGoal"])]
        
        elif filter_option == "Not Funded":
            filtered_campaigns = [c for c in filtered_campaigns 
                               if float(c["currentAmount"]) < float(c["fundingGoal"])]
        
        # Sort campaigns
        sort_option = st.selectbox("Sort by", 
                                ["Newest", "Oldest", "Most Funded", "Ending Soon"])
        
        if sort_option == "Newest":
            # Assuming campaign IDs are sequential
            filtered_campaigns = sorted(filtered_campaigns, key=lambda c: c["id"], reverse=True)
        
        elif sort_option == "Oldest":
            filtered_campaigns = sorted(filtered_campaigns, key=lambda c: c["id"])
        
        elif sort_option == "Most Funded":
            filtered_campaigns = sorted(filtered_campaigns, key=lambda c: float(c["currentAmount"]), reverse=True)
        
        elif sort_option == "Ending Soon":
            import time
            current_time = int(time.time())
            # Filter active campaigns and sort by time remaining
            active_campaigns = [c for c in filtered_campaigns if c["deadline"] > current_time]
            filtered_campaigns = sorted(active_campaigns, key=lambda c: c["deadline"])
        
        # Display campaigns
        if filtered_campaigns:
            st.write(f"Found {len(filtered_campaigns)} campaigns")
            
            # Display campaigns in a grid layout
            cols = st.columns(3)
            
            for i, campaign in enumerate(filtered_campaigns):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.subheader(campaign["title"])
                        st.write(campaign["description"][:150] + "..." if len(campaign["description"]) > 150 else campaign["description"])
                        
                        # Progress bar
                        progress = campaign["currentAmount"] / campaign["fundingGoal"] if campaign["fundingGoal"] > 0 else 0
                        st.progress(min(progress, 1.0))
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"💰 {campaign['currentAmount']} / {campaign['fundingGoal']} ETH")
                        
                        with col2:
                            time_left = calculate_time_left(campaign["deadline"])
                            st.write(f"⏱️ {time_left}")
                        
                        st.write(f"🧑‍💻 Creator: {format_address(campaign['creator'])}")
                        
                        st.button("View Details", key=f"view_{campaign['id']}", 
                                 on_click=lambda id=campaign['id']: st.switch_page("pages/campaign_details.py"))
        else:
            st.info("No campaigns found matching your criteria")
            
    else:
        st.error("Failed to fetch campaigns from the API")
        
except Exception as e:
    st.error(f"Error connecting to the backend: {str(e)}")
    st.info("Make sure the backend API is running at http://localhost:8000")

# Display Footer
Footer()
