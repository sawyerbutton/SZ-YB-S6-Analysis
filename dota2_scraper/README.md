# Dota 2 玩家数据爬取工具

使用 OpenDota API 获取玩家最近100场比赛的英雄使用频次、KDA等数据。

## 功能特点

- 📊 获取最近100场比赛数据
- 🦸 统计英雄使用频次和胜率
- 📈 计算KDA比率和平均数据
- 📁 输出JSON、CSV和TXT三种格式报告
- 🏆 按队伍整理数据

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行脚本

```bash
python dota2_player_stats.py
```

### 3. 查看结果

运行完成后会生成三个文件：
- `dota2_stats_YYYYMMDD_HHMMSS.json` - 完整JSON数据
- `dota2_stats_YYYYMMDD_HHMMSS.csv` - CSV汇总表格（可用Excel打开）
- `dota2_hero_report_YYYYMMDD_HHMMSS.txt` - 详细文本报告

## 输出数据说明

### 英雄统计
- **games**: 使用场次
- **wins**: 胜场数
- **win_rate**: 胜率
- **avg_kda**: 平均KDA

### 玩家统计
- **total_matches**: 总比赛数
- **win_rate**: 总体胜率
- **kda_ratio**: KDA比率 = (击杀+助攻)/死亡
- **top_heroes**: 最常用的10个英雄

## 配置说明

### 修改玩家列表

编辑 `dota2_player_stats.py` 中的 `TEAMS` 字典：

```python
TEAMS = {
    1: {
        "name": "队伍1",
        "players": {
            "玩家昵称": account_id,  # 32位Account ID
        }
    },
    # ...
}
```

### Steam ID 转换

如果你只有64位Steam ID，需要转换为32位Account ID：

```python
account_id_32 = steam_id_64 - 76561197960265728
```

例如：
- Steam64: 76561198083800272
- Account ID: 76561198083800272 - 76561197960265728 = 123534544

### 调整请求参数

```python
REQUEST_DELAY = 1.5  # 请求间隔（秒），避免触发限流
MATCHES_LIMIT = 100  # 获取最近的比赛数量
```

## 注意事项

1. **隐私设置**: 玩家必须在Dota 2设置中开启「公开比赛数据」，否则无法获取数据

2. **API限制**: 
   - 无API Key: 60次/分钟
   - 有API Key: 申请后额度更高
   - 建议保持1.5秒以上的请求间隔

3. **数据时效**: OpenDota数据可能有几分钟到几小时的延迟

## API 文档

- OpenDota API: https://docs.opendota.com/
- STRATZ API: https://stratz.com/api (备选方案)

## 常见问题

### Q: 为什么某些玩家数据获取失败？
A: 可能原因：
1. 玩家隐私设置为不公开
2. Account ID 错误
3. 网络问题或API限流

### Q: 如何获取更多历史数据？
A: 修改 `MATCHES_LIMIT` 参数，最大可设置较大值，但建议不超过500场

### Q: 英雄名称显示为ID怎么办？
A: 脚本会自动获取英雄名称映射，如果显示ID说明API调用失败，请检查网络

## 缺失的玩家ID

以下玩家Steam ID仍需补充：
- 队伍1: JY.LIU
- 队伍3: 海柱哥, will, walker
- 队伍4: 烟火声
- 队伍6: wei, 刘能
- 队伍7: 六柒柒, CatU, 河粉

## License

MIT License
