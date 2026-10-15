# 空数据库

`schema.sql` 是完整结构，先运行 init 生成零业务数据的 `data/library.sqlite`。Python 3.10+ 标准库即可初始化，无服务器。

表：sources（来源绑定）、snapshots（每来源当前成功快照）、knowledge（知识摘要）、products（料号）、prices（价格）、annotations（用户注释）、operations（Odoo 操作记录）。所有业务表均为空。

首次 `init` 拒绝覆盖已有数据库。`refresh` 仅更新 sources/snapshots；其余表由 agent 在业务核验后用参数化 SQL 和事务写入。所有连接先设置 `PRAGMA foreign_keys=ON`。

知识/产品/价格记录必须填 source_id、source_locator、source_revision、verified_at。未知版本可填 `unknown` 并说明；不能宣称已核对版本。稳定业务主键 id 由本地生成，Odoo 标识另放 source_locator/operations.remote_id，不与本地 id 混淆。

写入示例仅展示参数化方式，不是待导入业务数据：

```python
import sqlite3
with sqlite3.connect('data/library.sqlite') as db:
    db.execute('PRAGMA foreign_keys=ON')
    # values 必须来自已核实的数据，禁止把示例自动填入生产库。
    # db.execute('INSERT INTO knowledge(id,title,summary,source_id,source_locator,source_revision,verified_at) VALUES(?,?,?,?,?,?,?)', values)
```

价格 amount 使用十进制文本；min_qty/max_qty 亦使用十进制文本。日期使用 YYYY-MM-DD；读取/核验时间使用 UTC ISO 8601。更新业务记录时保留 annotations，不覆盖原系统。多人使用建议各自建库；本 SQLite 文件不是多人写入服务。
