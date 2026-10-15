# 销售资料库自建包

本包用于从零建立自己的知识库、料号库、价格库，并通过 AI 协助查询和操作 Odoo。提供 Skill、空数据库结构、配置模板和飞书只读刷新脚本。使用者自行提供资料、账号、权限和连接工具。

## 快速开始

从 GitHub 的 Code → Download ZIP 下载并解压，或克隆仓库。用 AI 客户端打开项目目录，安装 Python 3.10+ 后运行：

```sh
python scripts/library.py init
python scripts/library.py status
```

七张表应全部为零行。GitHub 源码版用 schema.sql 生成空库；不会分发运行数据库。init 不覆盖已有库。

把 `skills/sales-library-workspace` 复制到客户端 skills 目录，或让 AI 直接阅读其中的 SKILL.md。保留完整项目目录，脚本、配置和结构文件也在这里。

可直接给 AI：

> 使用 sales-library-workspace，从本项目的空库开始。先检查我提供的资料与已登录系统，协助绑定知识、料号和价格来源，再验证一次读取。Odoo 先做只读能力检查，列出可用的查询和单据操作。不要导入示例业务数据。

## 绑定来源

复制 `config/sources.example.json` 为 `config/sources.json`，按 [来源说明](skills/sales-library-workspace/references/sources.md) 填写自己的来源。飞书自动读取需要可用的 lark-cli 和本人账号权限。

```sh
python scripts/library.py refresh --source YOUR_SOURCE_ID
```

Odoo 用户复制 `config/odoo.example.json` 为 `config/odoo.json`，由 AI 根据实际实例配置。Odoo 模块是操作流程，依赖现有连接器或浏览器，不包含通用 API 写入程序。

飞书外用户可以下载本项目、用自己的文件或系统建库；下载不代表获得原组织的文档或 Odoo 权限。没有飞书也可使用空库和操作方法，但自动刷新脚本目前仅适配飞书。PDF 解析和业务字段入库需要单独核验。

## 使用边界

采用按需读取，没有定时服务。来源快照和结构化业务记录分开，读取成功不代表报价有效。创建/修改 Odoo 单据、提交和发送按使用者明确授权执行，并查回结果。填入真实资料后不要将工作目录直接公开。

说明：本版尚未选择开源许可证，公开可见不等于获得任意修改、再分发授权。当前 Skill 正文为中文，英文 README 提供安装与能力说明。
