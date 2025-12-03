#!/usr/bin/env python3
"""
Populate SS58 addresses for wallet and hotkeys
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('api_server/.env')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'leadsorcerer2024'),
    'database': os.getenv('DB_NAME', 'lead_generate'),
    'charset': 'utf8mb4'
}

# Address mappings
WALLET_ADDRESS = '5DtRdKKJRShvbJKDibUNfexfU9kBtz8KCNy3CDFvguCN3zHP'

HOTKEY_ADDRESSES = {
    'lion1998112310': '5HmP4wetYzX7FU2sLA4JYe9WEveFpQPqQLwsxm4113hPwBji',
    'lion199811239': '5Gb55afmfZZNGkmXDrfcC3MM2vRHWtGapGZdr2Bvz3D9eSjr',
    'lion199811238': '5GvayJX2cxKfa7huDwXsdLn1e2BBRVTZE29Cr9Jv4NXzNmSm',
    'lion199811237': '5DedLzjG9qbMm2zHNpZy3tmJVpXasHvvihosj7xYG4xJobNs',
    'lion199811235': '5G3bs8vhgWvR1oGreWmtuxTrxqT1XExLrvVhJ5e1TaRNxxqG',
    'lion199811234': '5CwmbbqE5kJZiq5KgDniUreA7t4hviizmC42uhgy9EYAocpL',
    'lion199811233': '5DvvWGXeWhSr93Vbg3hRp9FPPMQXCP1cX2nJJ3GrChTgGgr3',
    'lion199811232': '5GQTSus4ZdGpsJvwjn591MHQSfSUuTnDmVWuB3pheuRmFMNe',
}

def populate_addresses():
    """Populate SS58 addresses in the database."""
    conn = None
    try:
        print("Connecting to database...")
        conn = pymysql.connect(**DB_CONFIG)
        
        with conn.cursor() as cursor:
            # Update wallet address
            print(f"\n📝 Updating wallet address...")
            cursor.execute("""
                UPDATE wallets 
                SET wallet_address = %s
                WHERE wallet_name = 'jchb199811231'
            """, (WALLET_ADDRESS,))
            print(f"✅ Wallet address updated: {WALLET_ADDRESS}")
            
            # Update hotkey addresses
            print(f"\n📝 Updating hotkey addresses...")
            updated_count = 0
            for hotkey_name, address in HOTKEY_ADDRESSES.items():
                cursor.execute("""
                    UPDATE hotkeys 
                    SET hotkey_address = %s
                    WHERE hotkey_name = %s
                """, (address, hotkey_name))
                
                if cursor.rowcount > 0:
                    print(f"✅ {hotkey_name}: {address}")
                    updated_count += 1
                else:
                    print(f"⚠️  {hotkey_name}: Not found in database")
            
            conn.commit()
            
            print(f"\n{'='*80}")
            print(f"✅ Successfully updated {updated_count} hotkey addresses")
            print(f"{'='*80}")
            
            # Verify the updates
            print(f"\n📊 Verification:")
            print(f"{'='*80}")
            
            cursor.execute("SELECT wallet_name, wallet_address FROM wallets")
            wallet = cursor.fetchone()
            print(f"\nWallet: {wallet[0]}")
            print(f"Address: {wallet[1]}")
            
            cursor.execute("SELECT hotkey_name, hotkey_address FROM hotkeys ORDER BY hotkey_name")
            hotkeys = cursor.fetchall()
            print(f"\nHotkeys ({len(hotkeys)} total):")
            for hk in hotkeys:
                status = "✅" if hk[1] else "❌"
                print(f"  {status} {hk[0]:<20} {hk[1] or 'No address'}")
            
            print(f"\n{'='*80}")
            print(f"✅ All addresses populated successfully!")
            print(f"{'='*80}")
            print(f"\n🌐 Refresh your browser at http://localhost:8080 to see the addresses!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import sys
    success = populate_addresses()
    sys.exit(0 if success else 1)

