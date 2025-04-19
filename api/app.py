from flask import Flask, request, jsonify
from web3 import Web3, HTTPProvider
import json
import os
import sys
import time
from api.utils import load_contract, get_contract_address

# Add parent directory to path to import models
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from models import db, User, OffChainCampaign, Comment, UserActivity, Contribution

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Connect to Ethereum node - Sepolia testnet
INFURA_KEY = os.getenv("INFURA_KEY", "")
DEV_MODE = INFURA_KEY == ""  # Run in dev mode if no Infura key is provided

if not DEV_MODE:
    try:
        w3 = Web3(HTTPProvider(f"https://sepolia.infura.io/v3/{INFURA_KEY}"))
        
        # Contract setup
        CONTRACT_ADDRESS = get_contract_address()
        contract_abi = load_contract()
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
    except Exception as e:
        print(f"Error connecting to Ethereum: {e}")
        DEV_MODE = True  # Fallback to dev mode
else:
    print("Running API in development mode with sample data (no blockchain connection)")
    w3 = None
    contract = None

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get all campaigns from the blockchain"""
    try:
        if DEV_MODE:
            # Sample data for development mode
            campaigns = [
                {
                    'id': 0,
                    'creator': '0x1234567890123456789012345678901234567890',
                    'title': 'Sample Campaign 1',
                    'description': 'This is a sample campaign for testing purposes',
                    'imageUrl': 'https://picsum.photos/800/500',
                    'fundingGoal': 5.0,
                    'currentAmount': 2.5,
                    'deadline': int(time.time()) + 604800,  # 1 week from now
                    'claimed': False,
                    'exists': True
                },
                {
                    'id': 1,
                    'creator': '0x2345678901234567890123456789012345678901',
                    'title': 'Sample Campaign 2',
                    'description': 'Another sample campaign with more details',
                    'imageUrl': 'https://picsum.photos/800/500?random=2',
                    'fundingGoal': 10.0,
                    'currentAmount': 7.5,
                    'deadline': int(time.time()) + 1209600,  # 2 weeks from now
                    'claimed': False,
                    'exists': True
                }
            ]
        else:
            # Real blockchain data
            campaign_count = contract.functions.campaignCount().call()
            campaigns = []
            
            for i in range(campaign_count):
                campaign = contract.functions.getCampaign(i).call()
                campaign_data = {
                    'id': i,
                    'creator': campaign[0],
                    'title': campaign[1],
                    'description': campaign[2],
                    'imageUrl': campaign[3],
                    'fundingGoal': w3.from_wei(campaign[4], 'ether'),
                    'currentAmount': w3.from_wei(campaign[5], 'ether'),
                    'deadline': campaign[6],
                    'claimed': campaign[7],
                    'exists': campaign[8]
                }
                campaigns.append(campaign_data)
        
        return jsonify({"campaigns": campaigns, "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/campaigns/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get details of a specific campaign"""
    try:
        if DEV_MODE:
            # Sample data for development mode
            if campaign_id == 0:
                campaign_data = {
                    'id': 0,
                    'creator': '0x1234567890123456789012345678901234567890',
                    'title': 'Sample Campaign 1',
                    'description': 'This is a sample campaign for testing purposes',
                    'imageUrl': 'https://picsum.photos/800/500',
                    'fundingGoal': 5.0,
                    'currentAmount': 2.5,
                    'deadline': int(time.time()) + 604800,  # 1 week from now
                    'claimed': False,
                    'exists': True
                }
            elif campaign_id == 1:
                campaign_data = {
                    'id': 1,
                    'creator': '0x2345678901234567890123456789012345678901',
                    'title': 'Sample Campaign 2',
                    'description': 'Another sample campaign with more details',
                    'imageUrl': 'https://picsum.photos/800/500?random=2',
                    'fundingGoal': 10.0,
                    'currentAmount': 7.5,
                    'deadline': int(time.time()) + 1209600,  # 2 weeks from now
                    'claimed': False,
                    'exists': True
                }
            else:
                return jsonify({"error": "Campaign not found", "success": False}), 404
        else:
            # Real blockchain data
            campaign = contract.functions.getCampaign(campaign_id).call()
            campaign_data = {
                'id': campaign_id,
                'creator': campaign[0],
                'title': campaign[1],
                'description': campaign[2],
                'imageUrl': campaign[3],
                'fundingGoal': w3.from_wei(campaign[4], 'ether'),
                'currentAmount': w3.from_wei(campaign[5], 'ether'),
                'deadline': campaign[6],
                'claimed': campaign[7],
                'exists': campaign[8]
            }
        
        return jsonify({"campaign": campaign_data, "success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/campaigns/<int:campaign_id>/contribution/<address>', methods=['GET'])
def get_contribution(campaign_id, address):
    """Get contribution amount for a specific campaign and contributor"""
    try:
        if DEV_MODE:
            # Sample data for development mode
            if address.lower() == '0x1234567890123456789012345678901234567890'.lower():
                contribution_amount = 1.5 if campaign_id == 0 else 0.0
            elif address.lower() == '0x2345678901234567890123456789012345678901'.lower():
                contribution_amount = 0.5 if campaign_id == 0 else 3.0
            else:
                contribution_amount = 0.0
        else:
            # Real blockchain data
            contribution = contract.functions.getContribution(campaign_id, address).call()
            contribution_amount = w3.from_wei(contribution, 'ether')
            
        return jsonify({
            "contribution": contribution_amount,
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# Route for contract information
@app.route('/api/contract', methods=['GET'])
def get_contract_info():
    """Get contract address and ABI"""
    if DEV_MODE:
        # Sample contract information
        sample_address = "0x8123d34f5b52e8852cda1accac646b34dd4c77b5"
        sample_abi = load_contract()  # Use the same ABI for development
        return jsonify({
            "address": sample_address,
            "abi": sample_abi,
            "success": True
        })
    else:
        return jsonify({
            "address": CONTRACT_ADDRESS,
            "abi": contract_abi,
            "success": True
        })

# User routes
@app.route('/api/users', methods=['POST'])
def create_user():
    """Create or update a user profile"""
    try:
        data = request.json
        wallet_address = data.get('wallet_address')
        
        if not wallet_address:
            return jsonify({"error": "Wallet address is required", "success": False}), 400
        
        # Check if user already exists
        user = User.query.filter_by(wallet_address=wallet_address).first()
        
        if user:
            # Update existing user
            if 'username' in data:
                user.username = data.get('username')
            if 'email' in data:
                user.email = data.get('email')
            if 'profile_image' in data:
                user.profile_image = data.get('profile_image')
            if 'bio' in data:
                user.bio = data.get('bio')
        else:
            # Create new user
            user = User(
                wallet_address=wallet_address,
                username=data.get('username'),
                email=data.get('email'),
                profile_image=data.get('profile_image'),
                bio=data.get('bio')
            )
            db.session.add(user)
        
        db.session.commit()
        
        return jsonify({
            "user": {
                "id": user.id,
                "wallet_address": user.wallet_address,
                "username": user.username,
                "profile_image": user.profile_image
            },
            "success": True
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/users/<wallet_address>', methods=['GET'])
def get_user(wallet_address):
    """Get user profile by wallet address"""
    try:
        user = User.query.filter_by(wallet_address=wallet_address).first()
        
        if not user:
            return jsonify({"error": "User not found", "success": False}), 404
        
        return jsonify({
            "user": {
                "id": user.id,
                "wallet_address": user.wallet_address,
                "username": user.username,
                "email": user.email,
                "profile_image": user.profile_image,
                "bio": user.bio,
                "created_at": user.created_at
            },
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# Campaign metadata routes
@app.route('/api/campaign-metadata', methods=['POST'])
def create_campaign_metadata():
    """Create or update off-chain campaign metadata"""
    try:
        data = request.json
        print("Received data:", data)
        
        chain_id = data.get('chain_id') if data else None
        wallet_address = data.get('wallet_address') if data else None
        
        print(f"Chain ID: {chain_id}, Type: {type(chain_id)}")
        print(f"Wallet address: {wallet_address}")
        
        # Python treats 0 as falsy, but 0 is a valid chain_id, so we need a different check
        if chain_id is None or not wallet_address:
            return jsonify({"error": "Chain ID and wallet address are required", "success": False}), 400
        
        # Get user by wallet address
        user = User.query.filter_by(wallet_address=wallet_address).first()
        
        if not user:
            # Create user if doesn't exist
            user = User(wallet_address=wallet_address)
            db.session.add(user)
            db.session.flush()
        
        # Check if campaign metadata already exists
        campaign = OffChainCampaign.query.filter_by(chain_id=chain_id).first()
        
        if campaign:
            # Update existing campaign metadata
            campaign.title = data.get('title', campaign.title)
            campaign.description = data.get('description', campaign.description)
            campaign.image_url = data.get('image_url', campaign.image_url)
            campaign.category = data.get('category', campaign.category)
            campaign.tags = data.get('tags', campaign.tags)
            campaign.website = data.get('website', campaign.website)
            campaign.social_links = data.get('social_links', campaign.social_links)
        else:
            # Create new campaign metadata
            campaign = OffChainCampaign(
                chain_id=chain_id,
                creator_id=user.id,
                title=data.get('title'),
                description=data.get('description'),
                image_url=data.get('image_url'),
                category=data.get('category'),
                tags=data.get('tags'),
                website=data.get('website'),
                social_links=data.get('social_links')
            )
            db.session.add(campaign)
        
        db.session.commit()
        
        return jsonify({
            "campaign": {
                "id": campaign.id,
                "chain_id": campaign.chain_id,
                "title": campaign.title
            },
            "success": True
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/campaign-metadata/<int:chain_id>', methods=['GET'])
def get_campaign_metadata(chain_id):
    """Get off-chain campaign metadata by chain ID"""
    try:
        campaign = OffChainCampaign.query.filter_by(chain_id=chain_id).first()
        
        if not campaign:
            return jsonify({"error": "Campaign metadata not found", "success": False}), 404
        
        return jsonify({
            "campaign": {
                "id": campaign.id,
                "chain_id": campaign.chain_id,
                "creator_id": campaign.creator_id,
                "title": campaign.title,
                "description": campaign.description,
                "image_url": campaign.image_url,
                "category": campaign.category,
                "tags": campaign.tags,
                "website": campaign.website,
                "social_links": campaign.social_links,
                "updates": campaign.updates,
                "created_at": campaign.created_at
            },
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# Comment routes
@app.route('/api/campaigns/<int:chain_id>/comments', methods=['GET'])
def get_comments(chain_id):
    """Get comments for a campaign"""
    try:
        # Find the campaign
        campaign = OffChainCampaign.query.filter_by(chain_id=chain_id).first()
        
        if not campaign:
            return jsonify({"error": "Campaign not found", "success": False}), 404
        
        # Get top-level comments (no parent_id)
        comments = Comment.query.filter_by(campaign_id=campaign.id, parent_id=None).all()
        
        result = []
        for comment in comments:
            user = User.query.get(comment.user_id)
            
            # Get replies for this comment
            replies_list = []
            for reply in comment.replies:
                reply_user = User.query.get(reply.user_id)
                replies_list.append({
                    "id": reply.id,
                    "content": reply.content,
                    "user": {
                        "id": reply_user.id,
                        "wallet_address": reply_user.wallet_address,
                        "username": reply_user.username,
                        "profile_image": reply_user.profile_image
                    },
                    "created_at": reply.created_at
                })
            
            result.append({
                "id": comment.id,
                "content": comment.content,
                "user": {
                    "id": user.id,
                    "wallet_address": user.wallet_address,
                    "username": user.username,
                    "profile_image": user.profile_image
                },
                "created_at": comment.created_at,
                "replies": replies_list
            })
        
        return jsonify({
            "comments": result,
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/campaigns/<int:chain_id>/comments', methods=['POST'])
def create_comment(chain_id):
    """Create a comment for a campaign"""
    try:
        data = request.json
        wallet_address = data.get('wallet_address')
        content = data.get('content')
        parent_id = data.get('parent_id')
        
        if not wallet_address or not content:
            return jsonify({"error": "Wallet address and content are required", "success": False}), 400
        
        # Get user by wallet address
        user = User.query.filter_by(wallet_address=wallet_address).first()
        
        if not user:
            # Create user if doesn't exist
            user = User(wallet_address=wallet_address)
            db.session.add(user)
            db.session.flush()
        
        # Find the campaign
        campaign = OffChainCampaign.query.filter_by(chain_id=chain_id).first()
        
        if not campaign:
            return jsonify({"error": "Campaign not found", "success": False}), 404
        
        # Create comment
        comment = Comment(
            user_id=user.id,
            campaign_id=campaign.id,
            content=content,
            parent_id=parent_id
        )
        
        db.session.add(comment)
        
        # Record activity
        activity = UserActivity(
            user_id=user.id,
            activity_type='comment',
            campaign_id=chain_id,
            activity_data=json.dumps({"comment_id": comment.id})
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            "comment": {
                "id": comment.id,
                "content": comment.content,
                "user": {
                    "id": user.id,
                    "wallet_address": user.wallet_address,
                    "username": user.username,
                    "profile_image": user.profile_image
                },
                "created_at": comment.created_at
            },
            "success": True
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "success": False}), 500

# Contribution tracking
@app.route('/api/contributions', methods=['POST'])
def record_contribution():
    """Record a contribution to the database (mirror of blockchain data)"""
    try:
        data = request.json
        campaign_id = data.get('campaign_id')
        contributor_address = data.get('contributor_address')
        amount = data.get('amount')
        transaction_hash = data.get('transaction_hash')
        
        if not campaign_id or not contributor_address or not amount or not transaction_hash:
            return jsonify({"error": "Missing required fields", "success": False}), 400
        
        # Check if this transaction hash already exists
        existing = Contribution.query.filter_by(transaction_hash=transaction_hash).first()
        if existing:
            return jsonify({"error": "Transaction already recorded", "success": False}), 400
        
        # Create contribution record
        contribution = Contribution(
            campaign_id=campaign_id,
            contributor_address=contributor_address,
            amount=amount,
            transaction_hash=transaction_hash
        )
        
        db.session.add(contribution)
        
        # Get or create user
        user = User.query.filter_by(wallet_address=contributor_address).first()
        
        if not user:
            user = User(wallet_address=contributor_address)
            db.session.add(user)
            db.session.flush()
        
        # Record activity
        activity = UserActivity(
            user_id=user.id,
            activity_type='contribution',
            campaign_id=campaign_id,
            activity_data=json.dumps({"amount": amount, "transaction_hash": transaction_hash})
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            "contribution": {
                "id": contribution.id,
                "campaign_id": contribution.campaign_id,
                "contributor_address": contribution.contributor_address,
                "amount": contribution.amount,
                "transaction_hash": contribution.transaction_hash,
                "timestamp": contribution.timestamp
            },
            "success": True
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "success": False}), 500

# Create necessary database tables on startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
