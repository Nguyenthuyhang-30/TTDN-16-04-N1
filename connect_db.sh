#!/bin/bash
# Script để kết nối nhanh vào PostgreSQL container

echo "Đang kết nối vào PostgreSQL container..."
echo "Password: odoo"
echo ""

psql -h localhost -p 5434 -U odoo -d postgres

