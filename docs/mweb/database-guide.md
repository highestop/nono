> 需要了解 MWeb 的内部数据库结构，用于查询、分析或构建与 MWeb 数据交互的工具时，使用此指南。

## 基本内容

- MWeb `mainlib.db` SQLite 数据库的 schema 知识
- 表之间的关系和数据流
- 关键表的字段定义和数据类型
- 查询模式和常见用例

## 数据库概述

MWeb 将所有文档库数据存储在名为 `mainlib.db` 的 SQLite 数据库文件中，位于文档库根目录。

### 核心表

#### `article` - 文档元数据
- **用途**：存储文档库中所有文档的元数据
- **关键字段**：
  - `id` - 主键，自增
  - `uuid` - 文档的唯一标识符
  - `type` - 文档类型（markdown 等）
  - `state` - 文档状态（已发布、草稿等）
  - `docName` - 不含扩展名的文档文件名（通常为 NULL/空）
  - `dateAdd` - 文档创建时间戳
  - `dateModif` - 最后修改时间戳
  - `dateArt` - 文章日期时间戳

#### `cat` - 分类/文件夹结构
- **用途**：定义层级文件夹结构
- **关键字段**：
  - `id` - 主键，分类标识符
  - `name` - 分类/文件夹名称
  - `pid` - 父分类 UUID（用于层级关系，0 = 根分类）
  - `siteName` - 关联的站点名称
  - `siteURL` - 关联的站点 URL

#### `cat_article` - 分类与文档的关系
- **用途**：分类与文章之间的多对多关系
- **关键字段**：
  - `rid` - 外键，关联 `cat.uuid`
  - `aid` - 外键，关联 `article.uuid`

#### `tag` - 标签定义
- **用途**：存储所有可用标签
- **关键字段**：
  - `id` - 主键，标签标识符
  - `name` - 标签名称
  - `uuid` - 标签的唯一标识符

#### `tag_article` - 标签与文档的关系
- **用途**：标签与文章之间的多对多关系
- **关键字段**：
  - `rid` - 外键，关联 `tag.uuid`
  - `aid` - 外键，关联 `article.uuid`

#### `settings` - 应用配置
- **用途**：存储 MWeb 应用的设置和偏好
- **关键字段**：
  - 应用行为的配置键值对

## 常用查询模式

### 查找特定分类下的文档
```sql
SELECT a.* FROM article a
JOIN cat_article ca ON a.uuid = ca.aid
JOIN cat c ON ca.rid = c.uuid
WHERE c.name = 'CategoryName';
```

### 查找文档所属的所有分类
```sql
SELECT c.name FROM cat c
JOIN cat_article ca ON c.uuid = ca.rid
WHERE ca.aid = ?;  -- 此处使用 article.uuid
```

### 查找文档的所有标签
```sql
SELECT t.name FROM tag t
JOIN tag_article ta ON t.uuid = ta.rid
WHERE ta.aid = ?;  -- 此处使用 article.uuid
```

### 获取分类层级
```sql
WITH RECURSIVE category_tree AS (
  SELECT id, uuid, name, pid, 0 as level
  FROM cat WHERE pid = 0
  UNION ALL
  SELECT c.id, c.uuid, c.name, c.pid, ct.level + 1
  FROM cat c
  JOIN category_tree ct ON c.pid = ct.uuid
)
SELECT * FROM category_tree ORDER BY level, name;
```

## 适用场景

- 构建需要查询 MWeb 数据的工具之前
- 分析文档元数据和关系时
- 实现分类或标签管理功能之前
- 为集成目的理解 MWeb 数据模型时

## 约束

- 这是纯知识型技能——不执行数据库操作
- 数据库 schema 可能因 MWeb 版本不同而有所差异
- 修改前务必备份数据库
- 直接修改数据库可能影响 MWeb 应用的稳定性
