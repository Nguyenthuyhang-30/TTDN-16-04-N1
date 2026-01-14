#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để xem danh sách databases trong PostgreSQL container
Chạy: python view_databases.py
"""

import subprocess
import sys
from datetime import datetime

def get_databases():
    """Lấy danh sách databases từ PostgreSQL container"""
    try:
        # Chạy lệnh psql trong container
        cmd = [
            'docker', 'exec', 'postgres_odoo',
            'psql', '-U', 'odoo', '-d', 'postgres',
            '-c', "SELECT datname, pg_size_pretty(pg_database_size(datname)) as size, pg_database.datcollate as collate FROM pg_database WHERE datistemplate = false ORDER BY datname;"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Lỗi: {e.stderr}"
    except FileNotFoundError:
        return "Lỗi: Docker không được tìm thấy. Vui lòng đảm bảo Docker đã được cài đặt và đang chạy."

def get_detailed_info():
    """Lấy thông tin chi tiết về databases"""
    try:
        cmd = [
            'docker', 'exec', 'postgres_odoo',
            'psql', '-U', 'odoo', '-d', 'postgres',
            '-c', "\l"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Lỗi: {e.stderr}"
    except FileNotFoundError:
        return "Lỗi: Docker không được tìm thấy."

def get_table_count(db_name):
    """Đếm số lượng tables trong database"""
    try:
        cmd = [
            'docker', 'exec', 'postgres_odoo',
            'psql', '-U', 'odoo', '-d', db_name,
            '-c', "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Parse kết quả để lấy số
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if 'table_count' in line or line.strip().isdigit():
                continue
            if line.strip() and not line.startswith('-') and not line.startswith('('):
                return line.strip()
        return "N/A"
    except:
        return "N/A"

def main():
    print("=" * 70)
    print("DANH SÁCH DATABASES TRONG POSTGRESQL CONTAINER")
    print("=" * 70)
    print(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Container: postgres_odoo")
    print("=" * 70)
    print()
    
    # Lấy danh sách databases với thông tin size
    output = get_databases()
    print("DATABASES VÀ KÍCH THƯỚC:")
    print("-" * 70)
    print(output)
    print()
    
    # Lấy thông tin chi tiết
    print("THÔNG TIN CHI TIẾT:")
    print("-" * 70)
    detailed = get_detailed_info()
    print(detailed)
    print()
    
    # Lấy danh sách tên databases để đếm tables
    try:
        cmd = [
            'docker', 'exec', 'postgres_odoo',
            'psql', '-U', 'odoo', '-d', 'postgres',
            '-t', '-c', "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        db_names = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        if db_names:
            print("SỐ LƯỢNG TABLES TRONG MỖI DATABASE:")
            print("-" * 70)
            for db_name in db_names:
                if db_name and db_name != 'postgres':  # Bỏ qua database postgres mặc định
                    table_count = get_table_count(db_name)
                    print(f"  {db_name:30} : {table_count} tables")
    except:
        pass
    
    print()
    print("=" * 70)
    print("Để xem chi tiết tables trong một database cụ thể:")
    print("  docker exec -it postgres_odoo psql -U odoo -d <tên_database>")
    print("  Sau đó chạy: \\dt")
    print("=" * 70)

if __name__ == "__main__":
    main()

