#!/usr/bin/env python3
"""
Query CONSENSUS_RESULT events for a specific miner from the transparency_log table.

Usage:
    python scripts/feedback.py                    # Uses default MINER_HOTKEY
    python scripts/feedback.py <miner_hotkey>    # Query specific miner
    python scripts/feedback.py --all             # Show all event types
"""
import sys
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================
# MINER_HOTKEY = "5FujRaCjhSuhByr6z2qYtpSr6ESA6jHBgFsgP8PtJnepWq7T"  # Your miner hotkey
MINER_HOTKEY = "5FujRaCjhSuhByr6z2qYtpSr6ESA6jHBgFsgP8PtJnepWq7T"  # Your miner hotkey
MAX_RESULTS = 40

def get_supabase_client():
    """Initialize Supabase client"""
    from supabase import create_client

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')

    if not url or not key:
        print("❌ Error: SUPABASE_URL or SUPABASE_ANON_KEY not set in .env")
        sys.exit(1)

    return create_client(url, key)

def main():
    print("="*80)
    print("🔍 REJECTION FEEDBACK QUERY (via transparency_log)")
    print("="*80)
    print()

    print("🔌 Connecting to Supabase...")
    supabase = get_supabase_client()
    print("✅ Connected")
    print()

    print(f"📌 Querying CONSENSUS_RESULT events for miner: {MINER_HOTKEY[:20]}...")

    try:
        # Query transparency_log for CONSENSUS_RESULT events
        result = supabase.table("transparency_log") \
            .select("*") \
            .eq("event_type", "CONSENSUS_RESULT") \
            .order("ts", desc=True) \
            .limit(MAX_RESULTS) \
            .execute()

        all_events = result.data if result.data else []
        print(f"   Found {len(all_events)} CONSENSUS_RESULT events")
        for event in all_events:
            print(event)  
        # Filter for rejections related to this miner
        rejections = []
        for event in all_events:
            payload = event.get('payload', {})
            miner = payload.get('miner_hotkey', '')
            decision = payload.get('final_decision', '')

            # Filter by miner hotkey and rejected decision
            if miner == MINER_HOTKEY and decision == 'REJECTED':
                rejections.append(event)

        print(f"\n✅ Found {len(rejections)} rejection(s)\n")

        for idx, event in enumerate(rejections, 1):
            payload = event.get('payload', {})
            timestamp = event.get('ts', 'N/A')
            lead_id = payload.get('lead_id', 'N/A')
            rep_score = payload.get('final_rep_score', 'N/A')
            validator_count = payload.get('validator_count', 'N/A')
            rejection_reason = payload.get('primary_rejection_reason', 'Unknown')

            print(f"[{idx}] {timestamp}")
            print(f"    Lead ID: {lead_id}")
            print(f"    Rep Score: {rep_score}")
            print(f"    Validators: {validator_count}")
            print(f"    ❌ Rejection: {rejection_reason}")
            print()

        if not rejections:
            print("💡 No rejections found for this miner hotkey.")
            print(f"   Make sure MINER_HOTKEY is correct: {MINER_HOTKEY}")

    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()