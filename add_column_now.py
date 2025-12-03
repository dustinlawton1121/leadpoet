#!/usr/bin/env python3
import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='leadsorcerer2024',
    database='lead_generate',
    charset='utf8mb4'
)

try:
    with conn.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE wallets 
            ADD COLUMN wallet_address VARCHAR(255) DEFAULT NULL 
            COMMENT 'Wallet SS58 address (coldkey)' 
            AFTER wallet_name
        """)
        conn.commit()
        print("✅ Column added successfully")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("✅ Column already exists")
    else:
        print(f"❌ Error: {e}")
finally:
    conn.close()

