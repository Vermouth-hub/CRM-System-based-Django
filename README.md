# 客户信息管理系统

> 基于 Django 与 MySQL 构建的客户关系管理（CRM）课程设计项目。系统围绕客户全生命周期，将客户资料、支持服务、售后走访、投诉处理和新品反馈集中到统一的管理后台。

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-4479A1?logo=mysql&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-22C55E)

## 项目简介

这是一个面向企业客户服务场景的 Web 管理系统。项目采用 Django 的 MTV 架构组织业务逻辑与页面渲染，使用 MySQL 持久化业务数据，并提供响应式的后台管理界面。登录后，用户可以在仪表盘中快速查看关键业务数据，并进入各业务模块完成维护与处理。

## 功能一览

| 模块 | 功能 |
| --- | --- |
| 控制面板 | 汇总客户、服务、投诉与反馈等业务数据，展示近期统计信息。 |
| 客户资料管理 | 维护客户单位及其联系人、区域、满意度等基础资料，支持新增与检索。 |
| 客户支持管理 | 管理培训计划，支持技术文档上传、下载与删除。 |
| 售后服务管理 | 记录服务质量检查单、服务项目、负责人、服务时长与处理状态。 |
| 投诉管理 | 新建、查看并跟进客户投诉，记录关联客户、产品与处理进度。 |
| 新品市场反馈 | 收集客户对新品的正、负面反馈，为产品改进提供参考。 |
| 权限与会话 | 使用 Django 身份认证实现登录、退出与需要登录的页面保护。 |

## 技术栈

- 后端：Python、Django 5.1、Django REST framework
- 数据库：MySQL
- 前端：Django Templates、Tailwind CSS、Font Awesome
- 文件管理：Django `FileField` 与本地媒体目录

## 快速开始

### 1. 环境要求

- Python 3.10 或更高版本
- MySQL 8.0 或更高版本
- pip

### 2. 获取代码并创建虚拟环境

```powershell
git clone <你的仓库地址>
cd site\django

python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux 请使用：

```bash
source .venv/bin/activate
```

### 3. 安装依赖

```powershell
pip install "Django==5.1.7" djangorestframework django-cors-headers mysqlclient
```

> 若 Windows 环境下 `mysqlclient` 安装失败，可先安装 MySQL Connector/C 与 Visual C++ 生成工具，或根据本机环境选择兼容的 MySQL 驱动。

### 4. 配置数据库

在 MySQL 中创建数据库：

```sql
CREATE DATABASE management DEFAULT CHARACTER SET utf8mb4;
```

然后打开 `django/management/settings.py`，根据本机数据库修改 `DATABASES`：

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "management",
        "USER": "root",
        "PASSWORD": "你的数据库密码",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}
```

### 5. 初始化并运行

```powershell
python manage.py migrate
python manage.py createsuperuser  # 可选：创建 Django 管理员
python manage.py runserver
```

浏览器打开 [http://127.0.0.1:8000/](http://127.0.0.1:8000/) 即可进入系统；Django 管理后台地址为 [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)。

## 项目结构

```text
site/
├── README.md
└── django/
    ├── manage.py                 # Django 命令入口
    ├── management/               # 项目配置：设置、根路由、WSGI / ASGI
    └── backend/                  # 核心业务应用
        ├── models.py             # 客户、订单、服务、投诉等数据模型
        ├── views.py              # 页面渲染与业务处理
        ├── urls.py               # 业务路由
        ├── forms.py              # 文件上传表单
        ├── templates/            # 页面模板
        ├── static/               # 静态资源
        └── migrations/           # 数据库迁移记录
```

## 核心数据模型

系统以 `Company`（客户单位）为中心，并通过外键建立业务关联：

```text
Salesman ─┬─ Order ─── Company ─── Complaint
          │      │          │
          │      └─ Product ─┴─ NewProductFeedback
          ├─ Training
          └─ Service ── CheckItemDict
```

主要模型包括：`Salesman`、`Company`、`Product`、`Order`、`Training`、`Service`、`Complaint`、`NewProductFeedback` 与 `UploadedFile`。

## 开发说明

- 数据模型变更后执行 `python manage.py makemigrations` 与 `python manage.py migrate`。
- 开发环境使用 `DEBUG = True`；部署前请关闭调试模式、设置 `ALLOWED_HOSTS`，并通过环境变量管理 `SECRET_KEY` 和数据库凭据。
- 运行期间上传的文件位于媒体目录，应避免将真实业务文件提交到 Git 仓库。

---

如果这个项目对你有帮助，欢迎 Star ⭐ 或提出 Issue 交流改进建议。

