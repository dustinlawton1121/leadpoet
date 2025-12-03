import asyncio
import bittensor as bt
from Leadpoet.utils.cloud_db import (
    check_email_duplicate,
    gateway_get_presigned_url,
    gateway_upload_lead,
    gateway_verify_submission
)
from neurons.miner import sanitize_prospect

wallet = bt.wallet(name="jchb199811231", hotkey="lion199811231")

# List of leads
leads = [
    {
        "business": "Y Combinator",
        "full_name": "Lauren Caston",
        "first": "Lauren",
        "last": "Caston",
        "email": "lauren@ycombinator.com",
        "role": "Partner",
        "website": "http://www.ycombinator.com",
        "industry": "venture capital & private equity",
        "sub_industry": "Startup Accelerator",
        "region": "San Francisco, CA, USA",
        "linkedin": "http://www.linkedin.com/in/lgoldbergsf",
        "source_url": "hunter.io",
        "source_type": "hunter_domain_search",
        "description": "Y Combinator (YC) is a leading American technology startup accelerator and venture capital firm, founded in 2005 by Paul Graham, Jessica Livingston, Robert Tappan Morris, and Trevor Blackwell. It has been instrumental in launching over 5,000 companies, including notable names like Airbnb, Coinbase, and DoorDash. YC runs a rigorous three-month accelerator program four times a year, designed to support startups at various stages, from initial ideas to established companies.\n\nThe program offers seed funding, mentorship from experienced partners, and access to a vast investor network, helping startups enhance their products and fundraising capabilities. Founders also benefit from a strong community and alumni network, which provides valuable resources and connections. Additionally, YC operates Hacker News, a platform for technology discussions that serves both alumni and the broader tech community. With a focus on helping founders create products that meet market needs, Y Combinator has established itself as a powerhouse in the startup ecosystem.",
        "phone_numbers": ["+1 415-516-4158", "+14155164158"],
        "founded_year": 2005,
        "ownership_type": "Private",
        "company_type": "Corporation",
        "number_of_locations": 1,
        "socials": {
            "facebook": "https://www.facebook.com/YCombinator/",
            "linkedin": "http://www.linkedin.com/school/y-combinator",
            "twitter": "https://twitter.com/ycombinator"
        }
    },
    {
        "business": "Y Combinator",
        "full_name": "Andrew Miklas",
        "first": "Andrew",
        "last": "Miklas",
        "email": "andrew@ycombinator.com",
        "role": "General Partner",
        "website": "http://www.ycombinator.com",
        "industry": "venture capital & private equity",
        "sub_industry": "Startup Accelerator",
        "region": "San Francisco, CA, USA",
        "linkedin": "http://www.linkedin.com/in/amiklas",
        "source_url": "hunter.io",
        "source_type": "hunter_domain_search",
        "description": "Y Combinator (YC) is a leading American technology startup accelerator and venture capital firm, founded in 2005 by Paul Graham, Jessica Livingston, Robert Tappan Morris, and Trevor Blackwell. It has been instrumental in launching over 5,000 companies, including notable names like Airbnb, Coinbase, and DoorDash. YC runs a rigorous three-month accelerator program four times a year, designed to support startups at various stages, from initial ideas to established companies.\n\nThe program offers seed funding, mentorship from experienced partners, and access to a vast investor network, helping startups enhance their products and fundraising capabilities. Founders also benefit from a strong community and alumni network, which provides valuable resources and connections. Additionally, YC operates Hacker News, a platform for technology discussions that serves both alumni and the broader tech community. With a focus on helping founders create products that meet market needs, Y Combinator has established itself as a powerhouse in the startup ecosystem.",
        "phone_numbers": ["+1 415-516-4158", "+14155164158"],
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
]

def submit_lead(lead_data):
    """Submit a single lead"""
    # Sanitize
    sanitized = sanitize_prospect(lead_data, wallet.hotkey.ss58_address)
    
    # Check duplicate
    email = sanitized.get('email', '')
    if check_email_duplicate(email):
        print(f"⏭️  Skipping duplicate: {email}")
        return False
    
    # Get presigned URL
    presign_result = gateway_get_presigned_url(wallet, sanitized)
    if not presign_result:
        print(f"❌ Failed to get presigned URL for {email}")
        return False
    
    # Upload to S3
    if not gateway_upload_lead(presign_result['s3_url'], sanitized):
        print(f"❌ Failed to upload {email}")
        return False
    
    # Verify
    verification_result = gateway_verify_submission(wallet, presign_result['lead_id'])
    if verification_result:
        print(f"✅ Verified: {sanitized.get('business')} ({email})")
        return True
    else:
        print(f"❌ Verification failed: {email}")
        return False

# Submit all leads
import time

submitted_count = 0
for i, lead in enumerate(leads):
    if submit_lead(lead):
        submitted_count += 1

    # Wait 60 seconds between submissions (except after the last one)
    if i < len(leads) - 1:
        print(f"\n⏳ Waiting 60 seconds before next submission... ({i+1}/{len(leads)} completed)")
        time.sleep(60)

print(f"\n✅ Successfully submitted {submitted_count}/{len(leads)} leads")