#!/bin/bash
# Script để kiểm tra và hiển thị databases trong PostgreSQL container

echo "=========================================="
echo "KIỂM TRA DATABASES TRONG POSTGRESQL CONTAINER"
echo "=========================================="
echo ""

# Kiểm tra container có đang chạy không
if ! docker ps | grep -q postgres_odoo; then
    echo "❌ Container postgres_odoo không đang chạy!"
    echo "Chạy lệnh: docker-compose up -d"
    exit 1
fi

echo "✅ Container đang chạy"
echo ""
echo "Danh sách databases:"
echo "----------------------------------------"
docker exec postgres_odoo psql -U odoo -d postgres -c "\l" | grep -v template | grep -v "^-" | grep -v "rows)" | grep -v "Name" | grep -v "Access"

echo ""
echo "=========================================="
echo "THÔNG TIN KẾT NỐI CHO APP POSTGRESQL:"
echo "=========================================="
echo "Host: 127.0.0.1"
echo "Port: 5434"
echo "User: odoo"
echo "Password: odoo"
echo "Database: postgres (hoặc tên database cụ thể)"
echo "=========================================="

