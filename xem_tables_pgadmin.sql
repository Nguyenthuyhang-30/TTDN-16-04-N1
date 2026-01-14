-- Query để xem danh sách tables trong database nguyenhang.3010
-- Chạy query này trong Query Tool của pgAdmin

-- Xem tất cả tables
SELECT 
    table_schema,
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- Đếm số lượng tables
SELECT COUNT(*) as total_tables
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Xem 10 tables đầu tiên
SELECT table_name
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name
LIMIT 10;


