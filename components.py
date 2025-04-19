import streamlit as st
import json

class MetaMaskConnector:
    """Component for MetaMask wallet connection"""
    
    def render(self):
        wallet_container = st.container()
        
        with wallet_container:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.session_state.wallet_connected:
                    st.success(f"Connected: {st.session_state.wallet_address[:6]}...{st.session_state.wallet_address[-4:]}")
                else:
                    st.warning("Wallet not connected")
            
            with col2:
                if not st.session_state.wallet_connected:
                    connect_button = st.button("Connect MetaMask", use_container_width=True)
                    
                    if connect_button:
                        self._connect_wallet()
                else:
                    disconnect_button = st.button("Disconnect", use_container_width=True)
                    
                    if disconnect_button:
                        self._disconnect_wallet()
        
        # Add the JavaScript for MetaMask integration
        self._inject_web3_js()
    
    def _connect_wallet(self):
        """Set up state for wallet connection (actual connection happens in JS)"""
        st.session_state.connecting = True
    
    def _disconnect_wallet(self):
        """Disconnect wallet by resetting session state"""
        st.session_state.wallet_connected = False
        st.session_state.wallet_address = None
        st.rerun()
    
    def _inject_web3_js(self):
        """Inject JavaScript for MetaMask integration"""
        js_code = """
        <script src="https://cdn.jsdelivr.net/npm/web3@latest/dist/web3.min.js"></script>
        <script>
        async function connectWallet() {
            if (typeof window.ethereum !== 'undefined') {
                try {
                    // Request account access
                    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                    const account = accounts[0];
                    
                    // Check if we're on Sepolia testnet (chainId 11155111)
                    const chainId = await window.ethereum.request({ method: 'eth_chainId' });
                    
                    if (chainId !== '0xaa36a7') {
                        try {
                            // Try to switch to Sepolia
                            await window.ethereum.request({
                                method: 'wallet_switchEthereumChain',
                                params: [{ chainId: '0xaa36a7' }],
                            });
                        } catch (switchError) {
                            // If Sepolia is not added to MetaMask, add it
                            if (switchError.code === 4902) {
                                try {
                                    await window.ethereum.request({
                                        method: 'wallet_addEthereumChain',
                                        params: [{
                                            chainId: '0xaa36a7',
                                            chainName: 'Sepolia Test Network',
                                            nativeCurrency: {
                                                name: 'Sepolia ETH',
                                                symbol: 'ETH',
                                                decimals: 18
                                            },
                                            rpcUrls: ['https://sepolia.infura.io/v3/'],
                                            blockExplorerUrls: ['https://sepolia.etherscan.io']
                                        }],
                                    });
                                } catch (addError) {
                                    console.error(addError);
                                    return;
                                }
                            } else {
                                console.error(switchError);
                                return;
                            }
                        }
                    }
                    
                    // Update Streamlit component
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {
                            connected: true,
                            address: account
                        }
                    }, '*');
                    
                } catch (error) {
                    console.error(error);
                }
            } else {
                alert('MetaMask is not installed. Please install MetaMask to use this application.');
            }
        }

        // Set up listener for MetaMask account changes
        if (typeof window.ethereum !== 'undefined') {
            window.ethereum.on('accountsChanged', function (accounts) {
                if (accounts.length === 0) {
                    // User disconnected their wallet
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {
                            connected: false,
                            address: null
                        }
                    }, '*');
                } else {
                    // Account changed
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {
                            connected: true,
                            address: accounts[0]
                        }
                    }, '*');
                }
            });
        }
        
        // Check if we're trying to connect
        const streamlitDoc = window.parent.document;
        const buttons = streamlitDoc.querySelectorAll('button');
        for (const button of buttons) {
            if (button.innerText === 'Connect MetaMask') {
                button.addEventListener('click', connectWallet);
            }
        }
        </script>
        """
        st.components.v1.html(js_code, height=0)
        
        # Process messages from the frontend
        if "connected" in st.query_params:
            connected = st.query_params["connected"][0] == "true"
            address = st.query_params.get("address", [""])[0]
            
            st.session_state.wallet_connected = connected
            st.session_state.wallet_address = address if connected else None
            
            # Remove query parameters by rerunning
            st.query_params.clear()
            st.rerun()


class Header:
    """Header component with navigation"""
    
    def __init__(self):
        self.render()
    
    def render(self):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
            
            with col1:
                st.button("🏠 Home", use_container_width=True, 
                          on_click=lambda: st.switch_page("app.py"))
            
            with col2:
                st.button("🔍 Explore", use_container_width=True,
                         on_click=lambda: st.switch_page("pages/explore.py"))
            
            with col3:
                st.button("📝 Create", use_container_width=True,
                         on_click=lambda: st.switch_page("pages/create_campaign.py"))
            
            with col4:
                st.button("📊 Dashboard", use_container_width=True,
                         on_click=lambda: st.switch_page("pages/dashboard.py"))
            
            with col5:
                if st.session_state.wallet_connected:
                    st.write(f"👤 {st.session_state.wallet_address[:6]}...{st.session_state.wallet_address[-4:]}")
                else:
                    st.write("👤 Not connected")
            
            st.divider()


class Footer:
    """Footer component"""
    
    def __init__(self):
        self.render()
    
    def render(self):
        with st.container():
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**CryptoFund**")
                st.markdown("Decentralized Crowdfunding Platform")
            
            with col2:
                st.markdown("Running on Sepolia Testnet")
            
            with col3:
                st.markdown("© 2023 CryptoFund")
