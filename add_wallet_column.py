#!/usr/bin/env python3
"""
Simple script to add wallet_address column to wallets table.
Run this once to add the missing column.
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

def add_column():
    """Add wallet_address column to wallets table."""
    conn = None
    try:
        print(f"Connecting to database: {DB_CONFIG['database']}...")
        conn = pymysql.connect(**DB_CONFIG)
        
        with conn.cursor() as cursor:
            # Check if column exists
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE table_schema = %s
                AND table_name = 'wallets'
                AND column_name = 'wallet_address'
            """, (DB_CONFIG['database'],))
            
            result = cursor.fetchone()
            
            if result[0] > 0:
                print("✅ Column 'wallet_address' already exists")
                return True
            
            # Add column
            print("Adding column 'wallet_address'...")
            cursor.execute("""
                ALTER TABLE wallets 
                ADD COLUMN wallet_address VARCHAR(255) DEFAULT NULL 
                COMMENT 'Wallet SS58 address (coldkey)' 
                AFTER wallet_name
            """)
            
            conn.commit()
            print("✅ Column 'wallet_address' added successfully!")
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
    success = add_column()
    sys.exit(0 if success else 1)

