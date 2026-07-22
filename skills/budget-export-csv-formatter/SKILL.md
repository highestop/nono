---
name: budget-export-csv-formatter
description: Format CSV files exported from the Shark Bookkeeping Pro App into structured billing analysis
---

1. (Me) Export a CSV file from the Shark Bookkeeping Pro App and transfer it locally via AirDrop
2. (You) Convert the CSV file to UTF-8 encoding, for example by opening it in VSCode and saving it as UTF-8
3. (You) Run the `formatter.js` script, which generates the parsed CSV file in the same directory

**Input/output example:**

Input (TSV format exported from Shark Bookkeeping):
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

Usage examples:
- "Please format my billing file at ~/Downloads/budget-export.csv"
- "Use the billing formatter to process the CSV file I just AirDropped to Downloads"
