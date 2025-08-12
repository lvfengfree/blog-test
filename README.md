# 个人博客项目（测试版）

本项目是一个大学生的期末 Web 作业，当前为测试版，后续将继续更新完善。

## 技术栈

- Vue 3
- Flask
- MySQL

---

## 项目预览

![info](template/src/assets/read.png)

## 如何搭建此项目

### 1. 安装 Python 依赖

```shell
pip install -r requirements.txt
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

