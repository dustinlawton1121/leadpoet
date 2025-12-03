#!/usr/bin/env python3
"""
FIRST TO REGISTER - Race to be first in each new block
Monitors blocks and fires INSTANTLY when new block detected

Usage:
    source ./venv/bin/activate
    python first_1.py

Configuration:
    - USE_LOCAL_NODE = True: Uses local node at ws://127.0.0.1:9933 (ultra-low latency)
    - USE_LOCAL_NODE = False: Uses public RPC endpoint (fallback)
    - TAGET_BLOCK: Set to current block + 10 for immediate testing
"""

import os
import os.path
import sys
import asyncio
import websockets
import json
from datetime import datetime
from substrateinterface import SubstrateInterface
from dotenv import load_dotenv

try:
    from bittensor_wallet.keyfile import Keyfile
except ImportError:
    print("ERROR: bittensor_wallet not installed!")
    sys.exit(1)

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

WALLET_NAME = os.getenv("WALLET_NAME", "jchb199811231")
# HOTKEY_NAME = os.getenv("HOTKEY_NAME", "lion1998112310")
NETWORK = os.getenv("NETWORK", "finney")
NETUID = int(os.getenv("NETUID", "71"))
PASSWORD = os.getenv("PASSWORD", "")
LOCAL_NETWORK = os.getenv("LOCAL_NETWORK", "ws://127.0.0.1:9933")
PUBLIC_NETWORK = os.getenv("PUBLIC_NETWORK", "wss://entrypoint-finney.opentensor.ai:443")

# Multiple hotkeys - cycle through one per block!
HOTKEYS_NAMES = [
    "lion1998112310",
    "lion199811239",
    "lion199811238",
    "lion199811237",
    "lion199811235",
    "lion199811234"
]


# NO TIP - Pure speed only!
TIP = 0  # Rely on being FIRST, not highest tip

# LOCAL NODE - Ultra-low latency!
# Use local node for minimal network latency
USE_LOCAL_NODE = False  # Set to False to use public endpoints

if USE_LOCAL_NODE:
    ENDPOINTS = [
        LOCAL_NETWORK,  # Local Finney node
    ]
else:
    # Fallback to public endpoint
    ENDPOINTS = [
        PUBLIC_NETWORK,
    ]

# Target block for REAL registration on subnet 71

# ============================================================================
# INITIALIZE
# ============================================================================

print("=" * 70)
print("⚡ FIRST TO REGISTER - PURE SPEED MODE")
print("=" * 70)
print(f"Strategy: Fire INSTANTLY at start of each new block")
print(f"Tip: NONE - Pure speed only!")
print(f"Using LOCAL NODE: {USE_LOCAL_NODE}")
print(f"Endpoint: {ENDPOINTS[0]}")
print(f"Endpoints: {len(ENDPOINTS)} (parallel submission)")
print("=" * 70)

# Load wallet
print("\n[1/3] Loading wallet...")
wallet_path = os.path.expanduser(f"~/.bittensor/wallets/{WALLET_NAME}")
coldkey_keyfile = Keyfile(path=os.path.join(wallet_path, "coldkey"))

coldkey = coldkey_keyfile.get_keypair(password=PASSWORD)
print(f"  ✓ Coldkey: {coldkey.ss58_address}")

# Load all hotkeys
hotkeys = []
print(f"  ✓ Loading {len(HOTKEYS_NAMES)} hotkeys...")
for hotkey_name in HOTKEYS_NAMES:
    hotkey_keyfile = Keyfile(path=os.path.join(wallet_path, "hotkeys", hotkey_name))
    hotkey = hotkey_keyfile.get_keypair(password=PASSWORD)
    hotkeys.append({
        'name': hotkey_name,
        'keypair': hotkey,
        'address': hotkey.ss58_address
    })
    print(f"    - {hotkey_name}: {hotkey.ss58_address}")

print(f"  ✓ Total hotkeys loaded: {len(hotkeys)}")

# Connect
print(f"\n[2/2] Connecting...")
substrate = SubstrateInterface(
    url=ENDPOINTS[0],
    ss58_format=42,
    type_registry_preset='substrate-node-template',
)
print(f"  ✓ Connected: {substrate.chain}")
print(f"  ✓ Ready to register {len(hotkeys)} hotkeys on subnet {NETUID}!")

# ============================================================================
# RACE MODE
# ============================================================================

async def spam_mode():
    """
    SPAM MODE - Fire one registration per block, cycling through hotkeys
    """

    attempt = 0
    last_nonce = 31
    last_block = 0
    hotkey_index = 0  # Track which hotkey to use next

    print("\n" + "=" * 70)
    print("🔥 MULTI-HOTKEY REGISTRATION MODE")
    print("=" * 70)
    print(f"Cycling through {len(hotkeys)} hotkeys - one per block!")
    print("Press Ctrl+C to stop\n")

    # Get current nonce
    print("Getting extrinsics...")
    # account_info = substrate.query('System', 'Account', [coldkey.ss58_address])
    # last_nonce = account_info.value['nonce'] if account_info and account_info.value else 0
    # print(f"  ✓ Nonce: {last_nonce}")

    extrinsics = []
    new_block = 0

    # for i in range(3000000):
    #     new_block = substrate.get_block_number(substrate.get_block_hash())

    #     if new_block == TAGET_BLOCK - 1:
    #         break

    #     extrinsic = substrate.create_signed_extrinsic(
    #         call=call,
    #         keypair=coldkey,
    #         tip=0
    #     )

    #     extrinsics.append(extrinsic)

    print("Got extrinsics...")
    print("\n🔥 SUBSCRIBING TO NEW BLOCKS - REAL-TIME MODE")
    print("=" * 70)

    last_block = 0

    async with websockets.connect(ENDPOINTS[0]) as ws:

        # Subscribe to new block headers for INSTANT notifications
        subscribe_request = {
            "jsonrpc": "2.0",
            "method": "chain_subscribeNewHeads",
            "params": [],
            "id": 1
        }

        print("📡 Sending subscription request...")
        await ws.send(json.dumps(subscribe_request))

        # Get subscription ID
        response = await ws.recv()
        response_data = json.loads(response)
        subscription_id = response_data.get("result")

        print(f"✅ Subscribed! (ID: {subscription_id})")
        print(f"⏳ Listening for new blocks in REAL-TIME...\n")

        last_time = None

        # Listen for new block notifications
        while True:
            try:
                # Measure receive time
                recv_start = datetime.now()

                # Wait for new block notification (INSTANT - no polling delay!)
                message = await ws.recv()
                recv_end = datetime.now()
                recv_latency = (recv_end - recv_start).total_seconds() * 1000  # ms

                data = json.loads(message)

                 # Get current nonce
                account_info = substrate.query('System', 'Account', [coldkey.ss58_address])
                current_nonce = account_info.value['nonce'] if account_info and account_info.value else 0
                print(f"  ✓ Starting nonce: {current_nonce}")

                # Check if this is a block notification
                if "params" in data and "result" in data["params"]:
                    block_header = data["params"]["result"]
                    new_block = int(block_header["number"], 16)  # Convert hex to decimal

                    if new_block != last_block:
                        current_time = datetime.now()
                        timestamp = current_time.strftime("%H:%M:%S.%f")[:-3]

                        # Calculate time since last block
                        if last_time:
                            block_interval = (current_time - last_time).total_seconds()
                            print(f"\n[{timestamp}] 🆕 Block #{new_block} | Interval: {block_interval:.2f}s | Recv: {recv_latency:.1f}ms")
                        else:
                            print(f"\n[{timestamp}] 🆕 Block #{new_block} | Recv: {recv_latency:.1f}ms")

                        last_block = new_block
                        last_time = current_time

                        # 🚀 FIRE REGISTRATION WITH NEXT HOTKEY IN CYCLE!
                        current_hotkey = hotkeys[hotkey_index]
                        print(f"🚀 FIRING REGISTRATION for hotkey: {current_hotkey['name']}")

                        # Compose call for this specific hotkey
                        call = substrate.compose_call(
                            call_module='SubtensorModule',
                            call_function='burned_register',
                            call_params={
                                'netuid': NETUID,
                                'hotkey': current_hotkey['address'],
                            }
                        )

                        # Sign extrinsic with current nonce
                        extrinsic = substrate.create_signed_extrinsic(
                            call=call,
                            keypair=coldkey,
                            nonce=current_nonce,
                            tip=TIP
                        )
                        extrinsic_hex = str(extrinsic.data)

                        # Measure submission time
                        submit_start = datetime.now()

                        # Submit extrinsic via WebSocket (FASTEST method!)
                        submit_request = {
                            "jsonrpc": "2.0",
                            "method": "author_submitExtrinsic",
                            "params": [extrinsic_hex],
                            "id": new_block
                        }

                        await ws.send(json.dumps(submit_request))

                        # Wait for response
                        response = await ws.recv()
                        submit_end = datetime.now()
                        submit_latency = (submit_end - submit_start).total_seconds() * 1000

                        response_data = json.loads(response)

                        print(f"⏱️  Submission latency: {submit_latency:.1f}ms | Nonce: {current_nonce}")

                        if "result" in response_data:
                            tx_hash = response_data["result"]
                            print(f"✅ Transaction submitted! Hash: {tx_hash}")
                            print(f"🎯 Hotkey {current_hotkey['name']} registered successfully!")
                        elif "error" in response_data:
                            error = response_data["error"]
                            print(f"❌ Error: {error}")

                        # Move to next hotkey in cycle
                        hotkey_index = (hotkey_index + 1) % len(hotkeys)

                        print(f"📍 Next hotkey: {hotkeys[hotkey_index]['name']} (index {hotkey_index}/{len(hotkeys)-1})")

            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(0.1)

# Run
try:
    asyncio.run(spam_mode())
except KeyboardInterrupt:
    print("\n\n⏹️  Spam mode stopped")
    sys.exit(0)

