# 🚀 HƯỚNG DẪN TỰ DEPLOY API CHECK ID FREE FIRE LÊN VERCEL (100% MIỄN PHÍ)
> **Bản quyền & Phát triển bởi: Yan Dev**

Tự deploy API riêng giúp bot của bạn:
- ✅ **100% Ổn định**: Không phụ thuộc vào API công cộng (vốn hay bị sập hoặc quá tải).
- ✅ **Tốc độ cao**: Vercel Serverless phản hồi siêu nhanh (~200ms - 500ms).
- ✅ **Miễn phí vĩnh viễn**: Quota Vercel Hobby cấp tới 100GB băng thông và 100.000 lượt gọi/ngày hoàn toàn miễn phí.
- ✅ **Đầy đủ dữ liệu**: Trả về Rank, Rank CS, Like, Cấp độ, Thú cưng, Điểm uy tín, Tình trạng vi phạm PMT3 / Ban ID.

---

## ⚡ CÁCH 1: DEPLOY SIÊU TỐC VỚI 1 CLICK (KHUYÊN DÙNG - 1 PHÚT)

### Bước 1: Fork mã nguồn về GitHub của bạn
1. Mở trình duyệt và truy cập vào link GitHub nguồn:
   👉 **https://github.com/duyvinh09/FreeFireInfoSite**
2. Nhìn góc trên bên phải màn hình, bấm vào nút **Fork** -> Chọn **Create fork**.
   *(Kho lưu trữ sẽ được nhân bản sang tài khoản GitHub của bạn)*

### Bước 2: Liên kết và Deploy trên Vercel
1. Mở trang chủ Vercel: 👉 **https://vercel.com**
2. Đăng nhập bằng tài khoản GitHub của bạn.
3. Tại trang tổng quan (Dashboard), bấm nút **Add New...** (hoặc **New Project**) -> Chọn **Project**.
4. Bạn sẽ thấy danh sách repo, tìm `FreeFireInfoSite` và bấm nút **Import**.
5. Giữ nguyên toàn bộ cấu hình mặc định, bấm nút **Deploy**.
6. Đợi khoảng 30 - 45 giây để Vercel build dự án. Khi xuất hiện pháo hoa chúc mừng 🎉, bạn bấm vào **Continue to Dashboard** hoặc xem link Domain được cấp.

### Bước 3: Lấy link API và gắn vào Bot Discord
Link API của bạn sẽ có định dạng:
`https://<ten-project-cua-ban>.vercel.app/info?uid={}`
*(Hoặc `https://<ten-project-cua-ban>.vercel.app/player-info?region=VN&uid={}`)*

Mở file `.env` của bot (`c:\Users\Admin\Desktop\botshop\.env`) và điền:
```env
FREEFIRE_API_URL=https://<ten-project-cua-ban>.vercel.app/info?uid={}
```
Khởi động lại bot là xong!

---

## 🛠️ CÁCH 2: DÙNG BỘ SOURCE TỐI ƯU CÓ SẴN TẠI THƯ MỤC `botshop/freefire-api`

Thư mục `freefire-api` nằm ngay trong thư mục bot của bạn:
`c:\Users\Admin\Desktop\botshop\freefire-api`

Thư mục này đã được Yan Dev tinh chỉnh:
- Hỗ trợ cả 3 dạng endpoint: `/info?uid=...`, `/player-info?region=VN&uid=...`, `/api/freefire/info?uid=...`
- Tích hợp sẵn hơn 2.700 guest account Garena trong `accounts.txt`.
- Tự động fallback mã hóa AES (tương thích cả `pycryptodome` lẫn `cryptography`).

### Các bước đẩy lên GitHub riêng của bạn:
1. Vào **https://github.com/new** tạo một kho lưu trữ mới, đặt tên tuỳ ý (ví dụ: `my-ff-api`).
2. Mở PowerShell tại máy tính, gõ các lệnh sau:
   ```powershell
   cd c:\Users\Admin\Desktop\botshop\freefire-api
   git remote add origin https://github.com/<tai-khoan-github-cua-ban>/my-ff-api.git
   git push -u origin main
   ```
3. Lên **vercel.com** -> Bấm **Add New** -> **Project** -> Chọn `my-ff-api` -> Bấm **Deploy**.
4. Copy link do Vercel cấp và dán vào `.env` của bot!

---

## 🧪 KIỂM TRA API SAU KHI DEPLOY XONG

Bạn có thể test trực tiếp trên trình duyệt bằng cách nhập:
```text
https://<ten-project-cua-ban>.vercel.app/info?uid=1154264866
```
Nếu trình duyệt trả về chuỗi JSON chứa tên nhân vật, cấp độ, điểm rank và uy tín thì chúc mừng bạn, hệ thống API của bạn đã hoạt động 100%!
