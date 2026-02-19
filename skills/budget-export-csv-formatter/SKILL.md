---
name: budget-export-csv-formatter
description: 将鲨鱼记账 Pro App 导出的 CSV 文件格式化为结构化的账单分析
---

1. （我）在鲨鱼记账 Pro App 中导出 CSV 并通过 AirDrop 传输到本地
2. （你）将 CSV 文件转换为 UTF-8 编码（例如在 VSCode 中打开并以 UTF-8 保存）
3. （你）执行 [`@./scripts/formatter.js`](/skills/budget-export-csv-formatter/scripts/formatter.js) 脚本，将在同一目录生成解析后的 CSV 文件

**输入/输出示例：**

输入（鲨鱼记账导出的 TSV 格式）：
```
Time	Type	Category	Amount	Description
2024-01-15	支出	餐饮	25.50	午餐；麦当劳
2024-01-15	支出	交通	12.00	地铁；上班通勤
2024-01-16	收入	工资	5000.00	月薪；公司发放
2024-01-16	支出	餐饮	32.00	聚餐；火锅
```

输出（格式化后的 CSV）：
```csv
支出,餐饮,,57.5
,,聚餐,32
,,午餐,25.5
支出,交通,,12
,,地铁,12
收入,工资,,5000
,,月薪,5000
```

使用示例：
- "请格式化我在 ~/Downloads/budget-export.csv 的账单文件"
- "用账单格式化工具处理我刚 AirDrop 到 Downloads 的 CSV 文件"