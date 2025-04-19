import streamlit as st
import time
import datetime

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "wallet_connected" not in st.session_state:
        st.session_state.wallet_connected = False
    
    if "wallet_address" not in st.session_state:
        st.session_state.wallet_address = None
    
    if "campaigns" not in st.session_state:
        st.session_state.campaigns = []
    
    if "contract_address" not in st.session_state:
        st.session_state.contract_address = None
    
    if "contract_abi" not in st.session_state:
        st.session_state.contract_abi = None

def format_address(address):
    """Format Ethereum address for display"""
    if address:
        return f"{address[:6]}...{address[-4:]}"
    return "Unknown"

def format_deadline(timestamp):
    """Format Unix timestamp into a readable date"""
    if timestamp:
        date = datetime.datetime.fromtimestamp(timestamp)
        return date.strftime("%b %d, %Y")
    return "Unknown"

def format_timestamp(timestamp):
    """Convert Unix timestamp to a more readable format"""
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime("%Y-%m-%d %H:%M:%S")

def calculate_time_left(deadline):
    """Calculate time left until the deadline"""
    now = int(time.time())
    time_left = deadline - now
    
    if time_left <= 0:
        return "Ended"
    
    days_left = time_left // (24 * 3600)
    hours_left = (time_left % (24 * 3600)) // 3600
    
    if days_left > 0:
        return f"{days_left} days, {hours_left} hours left"
    else:
        return f"{hours_left} hours left"

def get_address_campaigns(address, campaigns):
    """Filter campaigns created by a specific address"""
    return [campaign for campaign in campaigns if campaign["creator"].lower() == address.lower()]

def get_backed_campaigns(address, campaigns):
    """Get campaigns that the user has backed"""
    # In a real implementation, this would query the blockchain for contributions
    # For this demo, we'll need to implement additional logic to track this
    return []

def wei_to_eth(wei_amount):
    """Convert wei to ether"""
    return float(wei_amount) / 10**18

def eth_to_wei(eth_amount):
    """Convert ether to wei"""
    return int(float(eth_amount) * 10**18)
