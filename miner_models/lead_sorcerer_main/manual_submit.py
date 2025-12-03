import sys
import os
from pathlib import Path
import json
from datetime import datetime, timezone

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

import bittensor as bt
from Leadpoet.utils.cloud_db import (
    check_email_duplicate,
    gateway_get_presigned_url,
    gateway_upload_lead,
    gateway_verify_submission
)
from neurons.miner import sanitize_prospect
from Leadpoet.utils.contributor_terms import (
    fetch_contributor_terms_from_github,
    create_attestation_record,
)

# Initialize your wallet
wallet = bt.wallet(name="jchb199811231", hotkey="lion199811238")

# Create attestation file if it doesn't exist
attestation_file = Path("data/regulatory/miner_attestation.json")
if not attestation_file.exists():
    print("📝 Creating attestation file...")
    attestation_file.parent.mkdir(parents=True, exist_ok=True)

    # Fetch current terms from GitHub
    try:
        terms_text, terms_hash = fetch_contributor_terms_from_github()
        print(f"✅ Fetched terms from GitHub (hash: {terms_hash[:16]}...)")

        # Create attestation record
        attestation = create_attestation_record(wallet.hotkey.ss58_address, terms_hash)

        # Save to file
        with open(attestation_file, 'w') as f:
            json.dump(attestation, f, indent=2)

        print(f"✅ Attestation file created: {attestation_file}")
    except Exception as e:
        print(f"❌ Failed to create attestation: {e}")
        print("   Continuing anyway (will use NOT_ATTESTED)...")
else:
    print(f"✅ Attestation file exists: {attestation_file}")

# lead_data = {
#   "business": "SpaceX",                    # REQUIRED
#   "full_name": "Elon Musk",                # REQUIRED
#   "first": "Elon",                         # REQUIRED
#   "last": "Musk",                          # REQUIRED
#   "email": "elon@spacex.com",              # REQUIRED
#   "role": "CEO",                           # REQUIRED
#   "website": "https://spacex.com",         # REQUIRED
#   "industry": "Aerospace Manufacturing",   # REQUIRED
#   "sub_industry": "Space Transportation",  # REQUIRED
#   "region": "Hawthorne, CA",               # REQUIRED
#   "linkedin": "https://linkedin.com/in/elonmusk", # REQUIRED
#   "source_url": "https://spacex.com/careers", # REQUIRED (URL where lead was found, OR "proprietary_database")
#   "source_type": "company_site",           # Source category
#   "description": "Aerospace manufacturer and space transportation company focused on reducing space transportation costs",
#   "phone_numbers": ["+1-310-363-6000"],
#   "founded_year": 2002,
#   "ownership_type": "Private",
#   "company_type": "Corporation",
#   "number_of_locations": 5,
#   "socials": {"twitter": "spacex"}
# }
lead_data = {
  "business": "Y Combinator",                    # REQUIRED
  "full_name": "Gustaf Alströmer",                # REQUIRED
  "first": "Gustaf",                         # REQUIRED
  "last": "Alströmer",                          # REQUIRED
  "email": "gustaf@ycombinator.com",              # REQUIRED
  "role": "General Partner",                           # REQUIRED
  "website": "http://www.ycombinator.com",         # REQUIRED
  "industry": "venture capital & private equity",   # REQUIRED
  "sub_industry": "Startup Accelerator",  # REQUIRED
  "region": "Mountain View, California, United States",               # REQUIRED
  "linkedin": "https://www.linkedin.com/in/gustafalstromer", # REQUIRED
  "source_url": "proprietary_database", # REQUIRED (URL where lead was found, OR "proprietary_database")
  "source_type": "proprietary_database",           # Source category
  "description": "Startup accelerator providing funding, mentorship, and resources to early-stage companies in the venture capital and private equity industry.",
  "phone_numbers": ["+1 415-516-4158"],
  "founded_year": 2005,
  "ownership_type": "Private",
  "company_type": "Corporation",
  "number_of_locations": 1,
  "socials": {
    "facebook": "https://www.facebook.com/YCombinator/",
    "linkedin": "http://www.linkedin.com/school/y-combinator",
    "twitter": "https://twitter.com/ycombinator"
  }
}

# Sanitize the lead (adds regulatory attestations)
sanitized_lead = sanitize_prospect(lead_data, wallet.hotkey.ss58_address)
print(f"Sanitized lead: {sanitized_lead}")
# Check for duplicates
email = sanitized_lead.get('email', '')
if check_email_duplicate(email):
    print(f"⏭️  Lead already exists: {email}")
    exit(1)

# Step 1: Get presigned URL
print("📝 Step 1: Getting presigned URL...")
presign_result = gateway_get_presigned_url(wallet, sanitized_lead)
if not presign_result:
    print("❌ Failed to get presigned URL")
    exit(1)

print(f"✅ Got presigned URL for lead: {presign_result['lead_id']}")

# Step 2: Upload to S3
print("📤 Step 2: Uploading to S3...")
s3_uploaded = gateway_upload_lead(presign_result['s3_url'], sanitized_lead)
if not s3_uploaded:
    print("❌ Failed to upload to S3")
    exit(1)

print("✅ Lead uploaded to S3")

# Step 3: Verify submission
print("🔍 Step 3: Verifying submission...")
verification_result = gateway_verify_submission(wallet, presign_result['lead_id'])

if verification_result:
    print(f"✅ SUCCESS! Lead verified and submitted")
    print(f"   Lead ID: {verification_result['lead_id']}")
    print(f"   Storage backends: {verification_result['storage_backends']}")
    print(f"   Submission time: {verification_result['submission_timestamp']}")
else:
    print("❌ Verification failed")