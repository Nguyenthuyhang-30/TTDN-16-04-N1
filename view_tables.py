#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để xem danh sách tables trong một database cụ thể
Sử dụng: python view_tables.py <tên_database>
Ví dụ: python view_tables.py nguyenhang.3010
"""

import subprocess
import sys
from datetime import datetime

def get_tables(db_name):
    """Lấy danh sách tables trong database"""
    try:
        cmd = [
            'docker', 'exec', 'postgres_odoo',
            'psql', '-U', 'odoo', '-d', db_name,
            '-c', "\dt"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Lỗi: {e.stderr}"
    except FileNotFoundError:
        return "Lỗi: Docker không được tìm thấy."

def get_table_info(db_name):
    """Lấy thông tin chi tiết về tables"""
    try:
        cmd = [
            'docker', 'exec', 'postgres_odoo',
            'psql', '-U', 'odoo', '-d', db_name,
            '-c', """
            SELECT 
                table_name,
                pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC
            LIMIT 20;
            """
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Lỗi: {e.stderr}"

def main():
    if len(sys.argv) < 2:
        print("Sử dụng: python view_tables.py <tên_database>")
        print("Ví dụ: python view_tables.py nguyenhang.3010")
        sys.exit(1)
    
    db_name = sys.argv[1]
    
    print("=" * 70)
    print(f"DANH SÁCH TABLES TRONG DATABASE: {db_name}")
    print("=" * 70)
    print(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Lấy danh sách tables
    tables = get_tables(db_name)
    print("DANH SÁCH TABLES:")
    print("-" * 70)
    print(tables)
    print()
    
    # Lấy thông tin kích thước
    print("TOP 20 TABLES LỚN NHẤT:")
    print("-" * 70)
    info = get_table_info(db_name)
    print(info)
    print("=" * 70)

if __name__ == "__main__":
    main()

