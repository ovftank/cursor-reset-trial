<div align="center">

# 🎯 Cursor Manager CLI

**Công cụ quản lý Cursor IDE mạnh mẽ và thân thiện**

[![PyPI version](https://badge.fury.io/py/cursor-manager.svg)](https://badge.fury.io/py/cursor-manager)
[![Python Version](https://img.shields.io/badge/python-≥3.10-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Windows Support](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)

[🚀 Tính Năng](#-tính-năng) •
[⚡ Cài Đặt](#-cài-đặt) •
[📖 Hướng Dẫn](#-hướng-dẫn) •
[📋 Yêu Cầu](#-yêu-cầu) •
[📄 Giấy Phép](#-giấy-phép)

</div>

## ✨ Tính Năng

- 🔄 **Làm Mới Cursor** - Tạo lại ID máy mới
- 🛑 **Tắt Tự Động Cập Nhật** - Không cho Cursor tự cập nhật
- 🧹 **Dọn Dẹp** - Xóa file tạm và rác
- ⬇️ **Hạ Cấp Xuống v0.44.11** - Quay về phiên bản cũ ổn định
- ⚡ **Tắt Nhanh** - Đóng hết Cursor đang chạy
- 🔑 **Làm Mới Tài Khoản** - Reset Trial Usage

## 🚀 Cài Đặt

### 📦 Từ PyPI

~~~bash
pip install -U cursor-manager
~~~

### 🛠️ Từ Source

~~~bash
git clone https://github.com/ovftank/cursor-reset-trial.git -b cli
cd cursor-reset-trial
pip install -e .
~~~

## 📖 Hướng Dẫn

### Menu Tương Tác

Chạy công cụ với giao diện menu dễ dùng:

~~~bash
cursor-manager
~~~

### Lệnh CLI

| Lệnh | Chức Năng |
|------|--------|
| `cursor-manager --help` | Xem hướng dẫn sử dụng |
| `cursor-manager reset` | Làm mới ID máy |
| `cursor-manager tat-update` | Tắt tự động cập nhật |
| `cursor-manager downgrade` | Hạ cấp xuống v0.44.11 |
| `cursor-manager xoa-cache` | Dọn dẹp file rác |
| `cursor-manager kill` | Tắt hết Cursor |
| `cursor-manager reset-tai-khoan` | Làm mới tài khoản |

## 📋 Yêu Cầu

- 🐍 Python ≥ 3.10
- 🪟 Windows
- 🔑 Quyền Admin (để chạy một số tính năng)

## 📄 Giấy Phép

Phần mềm này được phát hành theo [Giấy phép MIT](LICENSE).

---

<div align="center">

Được tạo với ❤️ bởi [ovftank](https://github.com/ovftank)

</div>
