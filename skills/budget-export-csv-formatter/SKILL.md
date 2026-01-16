---
name: budget-export-csv-formatter
description: Format exported CSV files from Shark Bookkeeping Pro App into structured budget analysis
---

1. Export CSV from 鲨鱼记账 Pro App and AirDrop to local
2. Format CSV file to UTF-8 encoding (e.g., open in VSCode and Save with UTF-8)
3. Execute `skills/budget-export-csv-formatter/scripts/formatter.js` script, will generate parsed CSV file in same directory

Input/Output example:

Input (TSV format from 鲨鱼记账):
```
Time	Type	Category	Amount	Description
2024-01-15	支出	餐饮	25.50	午餐；麦当劳
2024-01-15	支出	交通	12.00	地铁；上班通勤
2024-01-16	收入	工资	5000.00	月薪；公司发放
2024-01-16	支出	餐饮	32.00	聚餐；火锅
```

Output (formatted CSV):
```csv
支出,餐饮,,57.5
,,聚餐,32
,,午餐,25.5
支出,交通,,12
,,地铁,12
收入,工资,,5000
,,月薪,5000
```

Example usage:
- "Please format my budget file at ~/Downloads/budget-export.csv"
- "Use budget formatter to process the CSV file I just AirDropped to Downloads"