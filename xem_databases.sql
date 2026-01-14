-- Query để xem danh sách databases trong PostgreSQL
-- Chạy query này trong VS Code PostgreSQL tab

-- Xem tất cả databases
SELECT 
    datname as "Database Name",
    pg_size_pretty(pg_database_size(datname)) as "Size",
    datcollate as "Collate"
FROM pg_database 
WHERE datistemplate = false
ORDER BY datname;

-- Hoặc dùng lệnh psql:
-- \l


