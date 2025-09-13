# 个人博客项目（测试版）

本项目是一个大学生的期末 Web 作业，当前为测试版，后续将继续更新完善。

## 新增功能: Screenshot Selection Tool

新增了一个强大的截图选择工具，类似于微信、QQ 的截图功能：

### 功能特点
- ✅ 全屏截图捕获
- ✅ 拖拽选择区域功能
- ✅ 动态调整选择区域大小（8个控制手柄）
- ✅ 保存截图到本地
- ✅ AI处理接口（可扩展）
- ✅ Flask API 集成

### 使用方法

#### 独立使用
```shell
python3 screenshot_tool.py
```

#### API 接口
- `GET /api/screenshot/status` - 检查截图工具可用性
- `POST /api/screenshot/capture` - 捕获截图
- `POST /api/screenshot/save` - 保存截图

#### 演示
```shell
python3 demo_screenshot.py
```

## 技术栈

- Vue 3
- Flask
- MySQL
- Python Tkinter (截图工具界面)
- PIL (图像处理)

---

## 项目预览

![info](template/src/assets/read.png)

## 如何搭建此项目

### 1. 安装 Python 依赖

```shell
pip install -r requirements.txt
```

对于截图工具，还需要安装系统依赖：

```shell
# Ubuntu/Debian
sudo apt-get install python3-tk python3-pil python3-pil.imagetk scrot

# 或者使用其他截图工具
sudo apt-get install gnome-screenshot  # GNOME 桌面
sudo apt-get install imagemagick      # ImageMagick (import命令)
```

### 2. 进入前端模板目录并安装依赖

```shell
cd template
npm install
```

---

## 启动项目

### 开发环境

```shell
npm run dev
```

### 生产环境

```shell
npm run build
npm install -g serve
serve -s dist
```

---

## 配置数据库

请在 `app.py` 文件的第 10-13 行配置 MySQL 数据库信息。

---

## 创建数据库及所需表结构

```sql
CREATE DATABASE IF NOT EXISTS test;
USE test;

CREATE TABLE users (
username VARCHAR(255),
password VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS word_info (
title VARCHAR(255),
introduction LONGTEXT,
link LONGTEXT,
word LONGTEXT,
put_time DATE,
text_pinyin LONGTEXT
);
```

## 创建数据库及所需表结构

```sql
insert into users ("username","password") values ("输入你的管理员账号","密码");
```

