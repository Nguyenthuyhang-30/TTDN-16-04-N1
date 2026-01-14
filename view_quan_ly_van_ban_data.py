#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để xem dữ liệu module Quản lý văn bản trong PostgreSQL
"""

import subprocess
import sys

def run_sql(query, description):
    """Chạy SQL query và hiển thị kết quả"""
    try:
        cmd = [
            'docker', 'exec', 'postgres_odoo',
            'psql', '-U', 'odoo', '-d', 'nguyenhang.3010',
            '-c', query
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"\n{'='*70}")
        print(f"📋 {description}")
        print('='*70)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Docker không được tìm thấy. Vui lòng đảm bảo Docker đã được cài đặt và đang chạy.")
        return False

def main():
    print("="*70)
    print("📊 XEM DỮ LIỆU MODULE QUẢN LÝ VĂN BẢN TRONG POSTGRESQL")
    print("="*70)
    
    # Kiểm tra container
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=postgres_odoo', '--format', '{{.Names}}'],
            capture_output=True, text=True
        )
        if 'postgres_odoo' not in result.stdout:
            print("❌ Container postgres_odoo không đang chạy!")
            print("Chạy lệnh: docker-compose up -d")
            sys.exit(1)
    except FileNotFoundError:
        print("❌ Docker không được tìm thấy.")
        sys.exit(1)
    
    # Xem số lượng records
    run_sql(
        "SELECT 'Loại văn bản' as table_name, COUNT(*) as total FROM om_document_type UNION ALL SELECT 'Văn bản đến', COUNT(*) FROM om_document_incoming UNION ALL SELECT 'Văn bản đi', COUNT(*) FROM om_document_outgoing;",
        "TỔNG SỐ RECORDS"
    )
    
    # Xem dữ liệu Loại văn bản
    run_sql(
        "SELECT id, name, code, active FROM om_document_type ORDER BY id;",
        "LOẠI VĂN BẢN"
    )
    
    # Xem dữ liệu Văn bản đến
    run_sql(
        "SELECT id, name, number, date_received, status FROM om_document_incoming ORDER BY id;",
        "VĂN BẢN ĐẾN"
    )
    
    # Xem dữ liệu Văn bản đi
    run_sql(
        "SELECT id, name, number, date_sent, status FROM om_document_outgoing ORDER BY id;",
        "VĂN BẢN ĐI"
    )
    
    print("\n" + "="*70)
    print("✅ Hoàn tất!")
    print("="*70)
    print("\n💡 Lưu ý:")
    print("- Dữ liệu đã được lưu trong PostgreSQL database: nguyenhang.3010")
    print("- Các bảng:")
    print("  • om_document_type - Loại văn bản")
    print("  • om_document_incoming - Văn bản đến")
    print("  • om_document_outgoing - Văn bản đi")
    print("\n🔍 Để xem chi tiết hơn, bạn có thể:")
    print("  • Dùng VS Code PostgreSQL extension")
    print("  • Dùng pgAdmin")
    print("  • Chạy: psql -h localhost -p 5434 -U odoo -d nguyenhang.3010")

if __name__ == '__main__':
    main()

