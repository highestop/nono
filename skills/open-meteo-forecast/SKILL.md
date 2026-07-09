---
name: open-meteo-forecast
description: 使用无需授权的 Open-Meteo Forecast API 查询天气预报，适用于按经纬度或地点查询未来几小时或几天的温度、降水量、降水概率、风速等天气数据；不适用于需要商业 SLA、官方气象警报或已指定使用其他天气供应商的任务。
---

# Open-Meteo Forecast

- 免费 Forecast API 不需要 `API key`，直接请求 `https://api.open-meteo.com/v1/forecast`
- 对商业用途、高频请求或稳定性要求高的场景，提醒用户确认 Open-Meteo 的条款与付费方案
- 优先使用经纬度查询；只有用户只给地点名时，才用 Open-Meteo Geocoding API 查坐标
- 查询局部天气时，不要只用城市中心点；应按区县、街道或用户给定坐标分别查询
- Open-Meteo Geocoding API 对中文区县名可能不完整；如果地名不能匹配到目标行政区，必须改用明确坐标
- 回答必须说明数据源、坐标、时区、时间窗口和单位

## 工作流程

1. 明确用户要查的地点、时间窗口和指标，例如 `<未来 6 小时>`、`<未来 3 天>`、`<降水量>`、`<降水概率>`
2. 获取坐标：
   - 已有坐标：直接使用 `latitude` 和 `longitude`
   - 只有地点名：请求 `https://geocoding-api.open-meteo.com/v1/search?name={location}&count=10&language=zh&format=json`
   - 地点可能有歧义、缺失或匹配到错误行政区时，向用户确认或改用坐标
3. 请求 Forecast API：
   - 小时级：使用 `hourly=temperature_2m,precipitation_probability,precipitation,rain,showers,snowfall,weather_code,wind_speed_10m`
   - 天级：使用 `daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code`
   - 使用 `timezone={timezone}`，默认跟随用户时区或目标地点时区
4. 解析结果：
   - `precipitation`、`rain`、`showers` 单位通常为 `mm`
   - `snowfall` 单位通常为 `cm`
   - `precipitation_probability` 单位为 `%`
   - 未来 `<N>` 小时应取当前时间之后、`N` 小时窗口内的小时记录，并计算累计降水量
5. 输出结论：
   - 先给累计值和风险判断，再给小时明细
   - 区分“预计降水量”和“降水概率”
   - 说明这是模型预报，不等同于实时雷达或官方预警

## 可复用脚本

使用 [@skills/open-meteo-forecast/scripts/query_forecast.py](/skills/open-meteo-forecast/scripts/query_forecast.py) 查询小时级预报。

按坐标查询：

```bash
python3 skills/open-meteo-forecast/scripts/query_forecast.py \
  --label "北京市朝阳区" \
  --lat 39.9219 \
  --lon 116.4435 \
  --hours 6 \
  --timezone Asia/Shanghai
```

按地点名查询（ 必须检查输出里的 `geocoding.admin1`、`latitude` 和 `longitude` 是否符合预期 ）：

```bash
python3 skills/open-meteo-forecast/scripts/query_forecast.py \
  --location "北京市海淀区" \
  --hours 6 \
  --timezone Asia/Shanghai
```

指定一级行政区过滤：

```bash
python3 skills/open-meteo-forecast/scripts/query_forecast.py \
  --location "海淀" \
  --admin1 "北京市" \
  --hours 6 \
  --timezone Asia/Shanghai
```

输出为 JSON，重点字段：

| 字段 | 说明 |
|---|---|
| `label` | 查询地点标签 |
| `latitude` / `longitude` | 实际使用的坐标 |
| `timezone` | 结果时区 |
| `window_start` / `window_end` | 统计窗口 |
| `total_precipitation_mm` | 窗口内累计预计降水量 |
| `hourly[]` | 每小时的降水量、降水概率、温度、风速等 |

## API 示例

未来 6 小时降水：

```text
https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation,precipitation_probability,rain,showers&timezone={timezone}&forecast_days=2
```

未来 3 天日级预报：

```text
https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min,weather_code&timezone={timezone}&forecast_days=3
```

## GWT 示例

| Given | When | Then |
|---|---|---|
| 用户问“查北京市朝阳区未来 6 小时降雨量” | 使用地名或区中心坐标查询小时级 `precipitation` | 返回 6 小时累计降水量、逐小时明细、降水概率和坐标 |
| 用户问“未来 3 天北京几个区哪里雨更大” | 分别查询每个区的坐标和日级 `precipitation_sum` | 用表格比较各区 3 天累计降水量，并说明差异可信度 |
| 用户只给“北京” | 使用城市中心坐标，或询问是否要查具体区县 | 不把城市中心结果误称为全市每个局部地区 |
