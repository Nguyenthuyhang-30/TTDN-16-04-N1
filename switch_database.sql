-- Chuyển sang database nguyenhang.3010 để xem tables
-- Chạy lệnh này trong PSQL tab hoặc Query tab

-- Cách 1: Dùng lệnh psql
\c nguyenhang.3010

-- Sau đó xem tables:
\dt

-- Cách 2: Dùng SQL query để xem tables trong database nguyenhang.3010
-- (Chạy query này từ database postgres)
SELECT 
    table_schema,
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_catalog = 'nguyenhang.3010'
    AND table_schema = 'public'
ORDER BY table_name;


