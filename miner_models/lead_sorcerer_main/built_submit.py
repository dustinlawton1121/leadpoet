# In Python console or script
from neurons.miner import Miner, sanitize_prospect
import bittensor as bt

# Initialize miner
config = bt.config()
miner = Miner(config=config)

# Your lead
lead = {
    "business": "Test Company",
    "email": "test@company.com",
    # ... other fields
}

# Sanitize and submit
sanitized = sanitize_prospect(lead, miner.wallet.hotkey.ss58_address)

# Use the same submission code from sourcing_loop
from Leadpoet.utils.cloud_db import (
    gateway_get_presigned_url,
    gateway_upload_lead,
    gateway_verify_submission
)

presign_result = gateway_get_presigned_url(miner.wallet, sanitized)
gateway_upload_lead(presign_result['s3_url'], sanitized)
gateway_verify_submission(miner.wallet, presign_result['lead_id'])