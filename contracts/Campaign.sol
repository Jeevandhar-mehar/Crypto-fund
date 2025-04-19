// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title CrowdfundingPlatform
 * @dev Implements a decentralized crowdfunding platform where users can create and fund campaigns
 */
contract CrowdfundingPlatform {
    // Campaign structure
    struct Campaign {
        address creator;
        string title;
        string description;
        string imageUrl;
        uint256 fundingGoal;
        uint256 currentAmount;
        uint256 deadline;
        bool claimed;
        bool exists;
    }
    
    // Mapping from campaignId to Campaign
    mapping(uint256 => Campaign) public campaigns;
    
    // Mapping from campaignId to contributors and their contributions
    mapping(uint256 => mapping(address => uint256)) public contributions;
    
    // Total number of campaigns
    uint256 public campaignCount;
    
    // Events
    event CampaignCreated(uint256 indexed campaignId, address indexed creator, string title, uint256 fundingGoal, uint256 deadline);
    event ContributionMade(uint256 indexed campaignId, address indexed contributor, uint256 amount);
    event FundsClaimed(uint256 indexed campaignId, address indexed creator, uint256 amount);
    event FundsRefunded(uint256 indexed campaignId, address indexed contributor, uint256 amount);
    
    /**
     * @dev Creates a new campaign
     * @param _title Title of the campaign
     * @param _description Description of the campaign
     * @param _imageUrl URL of the campaign image
     * @param _fundingGoal Funding goal in wei
     * @param _durationInDays Duration of the campaign in days
     */
    function createCampaign(
        string memory _title,
        string memory _description,
        string memory _imageUrl,
        uint256 _fundingGoal,
        uint256 _durationInDays
    ) public {
        require(_fundingGoal > 0, "Funding goal must be greater than 0");
        require(_durationInDays > 0, "Duration must be greater than 0");
        
        uint256 campaignId = campaignCount;
        
        campaigns[campaignId] = Campaign({
            creator: msg.sender,
            title: _title,
            description: _description,
            imageUrl: _imageUrl,
            fundingGoal: _fundingGoal,
            currentAmount: 0,
            deadline: block.timestamp + (_durationInDays * 1 days),
            claimed: false,
            exists: true
        });
        
        campaignCount++;
        
        emit CampaignCreated(campaignId, msg.sender, _title, _fundingGoal, campaigns[campaignId].deadline);
    }
    
    /**
     * @dev Contribute to a campaign
     * @param _campaignId ID of the campaign
     */
    function contribute(uint256 _campaignId) public payable {
        Campaign storage campaign = campaigns[_campaignId];
        
        require(campaign.exists, "Campaign does not exist");
        require(block.timestamp < campaign.deadline, "Campaign has ended");
        require(msg.value > 0, "Contribution must be greater than 0");
        
        campaign.currentAmount += msg.value;
        contributions[_campaignId][msg.sender] += msg.value;
        
        emit ContributionMade(_campaignId, msg.sender, msg.value);
    }
    
    /**
     * @dev Creator claims funds if campaign is successful
     * @param _campaignId ID of the campaign
     */
    function claimFunds(uint256 _campaignId) public {
        Campaign storage campaign = campaigns[_campaignId];
        
        require(campaign.exists, "Campaign does not exist");
        require(msg.sender == campaign.creator, "Only creator can claim funds");
        require(block.timestamp >= campaign.deadline, "Campaign has not ended yet");
        require(campaign.currentAmount >= campaign.fundingGoal, "Funding goal not reached");
        require(!campaign.claimed, "Funds already claimed");
        
        campaign.claimed = true;
        
        // Transfer funds to the creator
        (bool success, ) = payable(campaign.creator).call{value: campaign.currentAmount}("");
        require(success, "Transfer failed");
        
        emit FundsClaimed(_campaignId, campaign.creator, campaign.currentAmount);
    }
    
    /**
     * @dev Contributor requests refund if campaign is unsuccessful
     * @param _campaignId ID of the campaign
     */
    function requestRefund(uint256 _campaignId) public {
        Campaign storage campaign = campaigns[_campaignId];
        
        require(campaign.exists, "Campaign does not exist");
        require(block.timestamp >= campaign.deadline, "Campaign has not ended yet");
        require(campaign.currentAmount < campaign.fundingGoal, "Funding goal reached, cannot refund");
        
        uint256 contributionAmount = contributions[_campaignId][msg.sender];
        require(contributionAmount > 0, "No contribution to refund");
        
        contributions[_campaignId][msg.sender] = 0;
        
        // Transfer funds back to the contributor
        (bool success, ) = payable(msg.sender).call{value: contributionAmount}("");
        require(success, "Transfer failed");
        
        emit FundsRefunded(_campaignId, msg.sender, contributionAmount);
    }
    
    /**
     * @dev Get campaign details
     * @param _campaignId ID of the campaign
     * @return Campaign details
     */
    function getCampaign(uint256 _campaignId) public view returns (
        address creator,
        string memory title,
        string memory description,
        string memory imageUrl,
        uint256 fundingGoal,
        uint256 currentAmount,
        uint256 deadline,
        bool claimed,
        bool exists
    ) {
        Campaign memory campaign = campaigns[_campaignId];
        return (
            campaign.creator,
            campaign.title,
            campaign.description,
            campaign.imageUrl,
            campaign.fundingGoal,
            campaign.currentAmount,
            campaign.deadline,
            campaign.claimed,
            campaign.exists
        );
    }
    
    /**
     * @dev Get contribution amount for a specific campaign and contributor
     * @param _campaignId ID of the campaign
     * @param _contributor Address of the contributor
     * @return Contribution amount
     */
    function getContribution(uint256 _campaignId, address _contributor) public view returns (uint256) {
        return contributions[_campaignId][_contributor];
    }
}
