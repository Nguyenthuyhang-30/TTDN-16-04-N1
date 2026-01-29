🎓 Khoa Công nghệ Thông tin - Trường Đại học Đại Nam
PLATFORM ERP
AIoTLab Logo FIT DNU Logo DaiNam University Logo

AIoTLab Faculty of Information Technology DaiNam University

Ubuntu Python Odoo PostgreSQL

HỆ THỐNG QUẢN LÝ DOANH NGHIỆP ERP
1. Giới thiệu
Platform ERP là hệ thống quản lý doanh nghiệp tổng hợp được xây dựng trên nền tảng Odoo 15.0, tích hợp các module quản lý nhân sự, khách hàng, văn bản và trợ lý AI thông minh. Hệ thống được phát triển bởi sinh viên Khoa Công nghệ Thông tin - Trường Đại học Đại Nam.

✨ Tính năng nổi bật
👥 Quản lý Nhân sự: Quản lý thông tin nhân viên, chấm công, lương, nghỉ phép
🤝 Quản lý Khách hàng: CRM, theo dõi khách hàng, phân khúc thị trường
📄 Quản lý Văn bản: Quản lý văn bản đến/đi, quy trình phê duyệt, chữ ký số
🤖 Trợ lý AI: Hỗ trợ tra cứu thông tin thông minh, chatbot tích hợp
2. Kiến trúc hệ thống
Kiến trúc hệ thống

2.1. Quản lý Nhân sự
🎯 Vai trò
Module Quản lý Nhân sự đóng vai trò trung tâm trong việc quản lý toàn bộ thông tin và hoạt động liên quan đến nhân viên trong doanh nghiệp.

⚙️ Chức năng
Chức năng	Mô tả
Quản lý nhân viên	Thêm, sửa, xóa thông tin nhân viên, phân bổ phòng ban
Chấm công	Theo dõi giờ làm việc, check-in/check-out
Tính lương	Tính toán lương, phụ cấp, khấu trừ tự động
Nghỉ phép	Tạo đơn nghỉ phép, quy trình phê duyệt, theo dõi số phép còn lại
Báo cáo	Thống kê nhân sự, báo cáo chấm công, lương
2.2. Quản lý Khách hàng
🎯 Vai trò
Module CRM giúp doanh nghiệp quản lý quan hệ khách hàng, theo dõi cơ hội kinh doanh và tối ưu hóa quy trình bán hàng.

⚙️ Chức năng
Chức năng	Mô tả
Quản lý khách hàng	Lưu trữ thông tin khách hàng, lịch sử giao dịch
Phân khúc khách hàng	Phân loại khách hàng theo tiêu chí
Theo dõi cơ hội	Quản lý pipeline bán hàng
Tương tác	Ghi nhận các hoạt động liên lạc với khách hàng
Báo cáo	Thống kê doanh số, hiệu quả bán hàng
2.3. Quản lý Văn bản
🎯 Vai trò
Module Quản lý Văn bản số hóa quy trình xử lý văn bản, đảm bảo tính minh bạch và hiệu quả trong công tác hành chính.

⚙️ Chức năng
Chức năng	Mô tả
Văn bản đến	Tiếp nhận, phân loại, chuyển xử lý văn bản đến
Văn bản đi	Soạn thảo, trình ký, phát hành văn bản đi
Quy trình phê duyệt	Workflow duyệt văn bản nhiều cấp
Chữ ký số	Ký số văn bản điện tử
Lưu trữ	Lưu trữ, tra cứu văn bản theo tiêu chí
3. Giao diện
3.1. Quản lý Nhân sự
Danh sách nhân viên
Giao diện quản lý nhân sự

3.2. Quản lý Khách hàng
Dashboard Khách hàng
Giao diện quản lý khách hàng

3.3. Quản lý Văn bản
Danh sách văn bản
Giao diện quản lý văn bản

3.4. Chữ ký số
Chữ ký số
Giao diện ký số văn bản

3.5. Trợ lý AI
Trợ lý AI
Giao diện Trợ lý AI thông minh

3.6. OCR Văn bản
Trợ lý AI
Giao diện OCR Văn bản

4. Sơ đồ nghiệp vụ
4.1. Quản lý Nhân sự
Sơ đồ nghiệp vụ Nhân sự
Quy trình nghiệp vụ Quản lý nhân sự

4.2. Quản lý Khách hàng
Sơ đồ nghiệp vụ Khách hàng
Quy trình quản lý khách hàng

4.3. Quản lý Văn bản
Sơ đồ nghiệp vụ Văn bản
Quy trình xử lý văn bản

5. Hướng dẫn cài đặt
5.1. Yêu cầu hệ thống
Hệ điều hành: Ubuntu 20.04+ / Windows 10+ / macOS
Python: 3.10+
PostgreSQL: 13+
RAM: Tối thiểu 4GB
Ổ cứng: Tối thiểu 10GB trống
5.2. Clone project
git clone https://gitlab.com/anhlta/odoo-fitdnu.git
cd odoo-fitdnu
5.3. Cài đặt thư viện hệ thống
sudo apt-get update
sudo apt-get install -y \
    libxml2-dev libxslt-dev libldap2-dev libsasl2-dev \
    libssl-dev python3.10-distutils python3.10-dev \
    build-essential libffi-dev zlib1g-dev \
    python3.10-venv libpq-dev
5.4. Khởi tạo môi trường ảo
python3.10 -m venv ./venv
source venv/bin/activate
pip3 install -r requirements.txt
5.5. Khởi tạo Database
docker-compose up -d
5.6. Cấu hình Odoo
Tạo file odoo.conf từ template:

cp odoo.conf.template odoo.conf
Nội dung file odoo.conf:

[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5432
db_name = ngoc
xmlrpc_port = 8069
5.7. Chạy hệ thống
python3 odoo-bin -c odoo.conf
Truy cập hệ thống tại: http://localhost:8069

6. Hướng dẫn sử dụng
6.1. Đăng nhập hệ thống
Truy cập http://localhost:8069
Nhập thông tin đăng nhập (admin/admin cho lần đầu)
Chọn module cần sử dụng từ menu Apps
6.2. Quản lý Nhân sự
Vào menu Nhân sự → Nhân Viên để xem danh sách nhân viên
Click Create để thêm nhân viên mới
Vào Nghỉ phép để quản lý đơn nghỉ phép
Vào Chấm công & Lương để theo dõi công và tính lương
6.3. Quản lý Khách hàng
Vào menu Khách hàng để xem danh sách khách hàng
Click Create để thêm khách hàng mới
Sử dụng các filter để phân loại khách hàng
6.4. Quản lý Văn bản
Vào menu Văn bản để xem danh sách văn bản
Click Create để tạo văn bản mới
Sử dụng workflow để trình ký và phê duyệt văn bản
6.5. Trợ lý AI
Click vào icon AI trên thanh menu
Nhập câu hỏi hoặc yêu cầu
AI sẽ hỗ trợ tra cứu thông tin từ hệ thống
7. Poster
Poster
Poster giới thiệu hệ thống Platform ERP

8. Liên hệ
👩‍💻 Thông tin tác giả
Thông tin	Chi tiết
Họ và tên	Nguyễn Thuý Hằng
Số điện thoại	0986972513
Email	nguyenthuyhang.qc2004@gmail.com
