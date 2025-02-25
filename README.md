<div align="center">

# 🎯 Cursor Manager CLI

**Công cụ quản lý Cursor IDE mạnh mẽ và linh hoạt**

[![PyPI version](https://badge.fury.io/py/cursor-manager.svg)](https://badge.fury.io/py/cursor-manager)
[![Python Version](https://img.shields.io/badge/python-≥3.10-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Windows Support](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)

[🚀 Tính Năng](#tính-năng) •
[⚡ Cài Đặt](#cài-đặt) •
[📖 Hướng Dẫn](#hướng-dẫn) •
[📋 Yêu Cầu](#yêu-cầu) •
[📄 Giấy Phép](#giấy-phép)

</div>

## ✨ Tính Năng

- 🔄 **Reset ID Máy** - Khởi tạo lại định danh máy
- 🛑 **Tắt Auto Update** - Vô hiệu hóa tự động cập nhật
- 🧹 **Xóa Cache** - Dọn dẹp bộ nhớ đệm
- ⬇️ **Tải Cursor v0.44.11** - Tải phiên bản ổn định
- ⚡ **Tắt Cursor** - Đóng tất cả tiến trình

## 🚀 Cài Đặt

### 📦 Từ PyPI

~~~bash
pip install cursor-manager
~~~

### 🛠️ Từ Source

~~~bash
git clone https://github.com/ovftank/cursor-reset-trial.git -b cli
cd cursor-reset-trial
pip install -e .
~~~

## 📖 Hướng Dẫn

### Menu Tương Tác

Chạy công cụ với giao diện menu tương tác:

~~~bash
cursor-manager
~~~

### Lệnh CLI

| Lệnh | Mô Tả |
|------|--------|
| `cursor-manager --help` | Xem hướng dẫn sử dụng |
| `cursor-manager info` | Xem phiên bản Cursor |
| `cursor-manager reset` | Reset ID và thông tin máy |
| `cursor-manager tat-update` | Tắt tự động cập nhật |
| `cursor-manager status` | Xem trạng thái chi tiết |
| `cursor-manager tai` | Tải Cursor v0.44.11 |
| `cursor-manager xoa-cache` | Xóa cache của Cursor |
| `cursor-manager kill` | Tắt tất cả tiến trình Cursor |

## 📋 Yêu Cầu

- 🐍 Python ≥ 3.10
- 🪟 Windows
- 🔑 Quyền Administrator (cho một số tính năng)

## 📄 Giấy Phép

Dự án này được phân phối dưới [Giấy phép MIT](LICENSE).

---

<div align="center">

Được tạo với ❤️ bởi [ovftank](https://github.com/ovftank)

</div>
