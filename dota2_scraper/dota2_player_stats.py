"""
Dota 2 玩家数据爬取工具
使用 OpenDota API 获取玩家最近100场比赛的英雄使用频次、KDA等数据
"""

import requests
import time
import json
from collections import defaultdict
from datetime import datetime
import csv

# ============== 配置区域 ==============

# 队伍和玩家数据
# 注意：如需补充缺失的Steam ID，请在对应位置添加
TEAMS = {
    1: {
        "name": "队伍1",
        "color": "#FFF2CC",  # 黄色系
        "players": {
            "思Kirara": 149901486,
            "德德": 216565503,
            "awe": 1101454493,
            "卡卡罗特": 124106189,
            # "JY.LIU": None,  # ⚠️ 缺失Steam ID
        }
    },
    2: {
        "name": "队伍2",
        "color": "#D5E8D4",  # 绿色系
        "players": {
            "ahji": 168908562,
            "Sam QL": 215850857,
            "清寒": 146510503,
            "阿边边边边边": 103091764,
            "VK": 117116280,
        }
    },
    3: {
        "name": "队伍3",
        "color": "#DAE8FC",  # 蓝色系
        "players": {
            "LiffyIsland": 301128180,
            "Ym": 138637714,
            # "海柱哥": None,  # ⚠️ 缺失
            # "will": None,  # ⚠️ 缺失
            # "walker": None,  # ⚠️ 缺失
        }
    },
    4: {
        "name": "队伍4",
        "color": "#E1D5E7",  # 紫色系
        "players": {
            "黄神AME": 225835718,
            "邮寄时光": 354739911,
            "看我干嘛": 136320131,
            "yuan.": 365587496,
            # "烟火声": None,  # ⚠️ 缺失
        }
    },
    5: {
        "name": "队伍5",
        "color": "#FFE6CC",  # 橙色系
        "players": {
            "Dom": 362233986,
            "老板": 294993528,
            "拉罗": 157552982,
            "EK": 136611464,
            "韭韭（时浅）": 402598895,
        }
    },
    6: {
        "name": "队伍6",
        "color": "#F8CECC",  # 红色系
        "players": {
            "彭律": 146348911,
            "世涛": 140976240,
            "Destiny": 86788193,
            # "wei": None,  # ⚠️ 缺失
            # "刘能": None,  # ⚠️ 缺失
        }
    },
    7: {
        "name": "队伍7",
        "color": "#B4A7D6",  # 淡紫色
        "players": {
            "水豚噜噜": 900466924,
            "含章可贞": 387262791,
            # "六柒柒": None,  # ⚠️ 缺失
            # "CatU": None,  # ⚠️ 缺失
            # "河粉": None,  # ⚠️ 缺失
        }
    },
    8: {
        "name": "队伍8",
        "color": "#A9D08E",  # 草绿色
        "players": {
            "老刘": 117116280,
            "百京泰迪熊": 141869520,
            "漆黑之牙-卓": 146389394,
            "WWW": 183746899,
            "A": 366757026,
        }
    },
}

# API 配置
BASE_URL = "https://api.opendota.com/api"
REQUEST_DELAY = 1.5  # 请求间隔（秒），避免触发限流
MATCHES_LIMIT = 100  # 获取最近的比赛数量

# ============== 英雄数据 ==============

def get_heroes_map():
    """获取英雄ID到名称的映射"""
    print("正在获取英雄列表...")
    url = f"{BASE_URL}/heroes"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        heroes = response.json()
        hero_map = {hero['id']: hero['localized_name'] for hero in heroes}
        print(f"成功获取 {len(hero_map)} 个英雄数据")
        return hero_map
    except Exception as e:
        print(f"获取英雄列表失败: {e}")
        return {}

# ============== 玩家数据获取 ==============

def get_player_info(account_id):
    """获取玩家基本信息"""
    url = f"{BASE_URL}/players/{account_id}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  获取玩家信息失败: {e}")
        return None

def get_player_matches(account_id, limit=100):
    """获取玩家最近的比赛记录"""
    url = f"{BASE_URL}/players/{account_id}/matches"
    params = {"limit": limit}
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  获取比赛记录失败: {e}")
        return []

def get_player_heroes(account_id):
    """获取玩家的英雄统计数据"""
    url = f"{BASE_URL}/players/{account_id}/heroes"
    try:
        response = requests.get(url, params={"limit": 20}, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  获取英雄统计失败: {e}")
        return []

def get_player_totals(account_id):
    """获取玩家总体统计"""
    url = f"{BASE_URL}/players/{account_id}/totals"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  获取总体统计失败: {e}")
        return []

# ============== 数据分析 ==============

def analyze_matches(matches, hero_map):
    """分析比赛数据"""
    if not matches:
        return None
    
    stats = {
        "total_matches": len(matches),
        "wins": 0,
        "losses": 0,
        "total_kills": 0,
        "total_deaths": 0,
        "total_assists": 0,
        "hero_usage": defaultdict(lambda: {"games": 0, "wins": 0, "kills": 0, "deaths": 0, "assists": 0}),
        "game_modes": defaultdict(int),
        "recent_matches": []
    }
    
    for match in matches:
        hero_id = match.get('hero_id', 0)
        hero_name = hero_map.get(hero_id, f"Unknown({hero_id})")
        
        # 判断胜负
        player_slot = match.get('player_slot', 0)
        radiant_win = match.get('radiant_win', False)
        is_radiant = player_slot < 128
        won = (is_radiant and radiant_win) or (not is_radiant and not radiant_win)
        
        if won:
            stats["wins"] += 1
            stats["hero_usage"][hero_name]["wins"] += 1
        else:
            stats["losses"] += 1
        
        # KDA统计
        kills = match.get('kills', 0) or 0
        deaths = match.get('deaths', 0) or 0
        assists = match.get('assists', 0) or 0
        
        stats["total_kills"] += kills
        stats["total_deaths"] += deaths
        stats["total_assists"] += assists
        
        # 英雄使用统计
        stats["hero_usage"][hero_name]["games"] += 1
        stats["hero_usage"][hero_name]["kills"] += kills
        stats["hero_usage"][hero_name]["deaths"] += deaths
        stats["hero_usage"][hero_name]["assists"] += assists
        
        # 游戏模式
        game_mode = match.get('game_mode', 0)
        stats["game_modes"][game_mode] += 1
        
        # 保存最近比赛详情
        if len(stats["recent_matches"]) < 10:
            stats["recent_matches"].append({
                "match_id": match.get('match_id'),
                "hero": hero_name,
                "kda": f"{kills}/{deaths}/{assists}",
                "won": won,
                "duration": match.get('duration', 0) // 60,  # 转换为分钟
                "start_time": datetime.fromtimestamp(match.get('start_time', 0)).strftime('%Y-%m-%d %H:%M') if match.get('start_time') else "N/A"
            })
    
    # 计算平均KDA
    total = stats["total_matches"]
    if total > 0:
        stats["avg_kills"] = round(stats["total_kills"] / total, 2)
        stats["avg_deaths"] = round(stats["total_deaths"] / total, 2)
        stats["avg_assists"] = round(stats["total_assists"] / total, 2)
        stats["win_rate"] = round(stats["wins"] / total * 100, 2)
        
        # KDA比率
        if stats["total_deaths"] > 0:
            stats["kda_ratio"] = round((stats["total_kills"] + stats["total_assists"]) / stats["total_deaths"], 2)
        else:
            stats["kda_ratio"] = stats["total_kills"] + stats["total_assists"]
    
    # 排序英雄使用频率
    sorted_heroes = sorted(stats["hero_usage"].items(), key=lambda x: x[1]["games"], reverse=True)
    stats["top_heroes"] = []
    for hero_name, hero_stats in sorted_heroes[:10]:  # 前10个常用英雄
        games = hero_stats["games"]
        wins = hero_stats["wins"]
        win_rate = round(wins / games * 100, 2) if games > 0 else 0
        avg_kda = f"{round(hero_stats['kills']/games, 1)}/{round(hero_stats['deaths']/games, 1)}/{round(hero_stats['assists']/games, 1)}" if games > 0 else "0/0/0"
        
        stats["top_heroes"].append({
            "hero": hero_name,
            "games": games,
            "wins": wins,
            "win_rate": win_rate,
            "avg_kda": avg_kda
        })
    
    return stats

# ============== 主程序 ==============

def fetch_all_players_data():
    """获取所有玩家数据"""
    print("=" * 60)
    print("Dota 2 玩家数据爬取工具")
    print("=" * 60)
    
    # 获取英雄映射
    hero_map = get_heroes_map()
    if not hero_map:
        print("警告: 无法获取英雄列表，将使用ID显示")
    
    time.sleep(REQUEST_DELAY)
    
    all_results = {}
    total_players = sum(len(team["players"]) for team in TEAMS.values())
    current = 0
    
    for team_id, team_data in TEAMS.items():
        team_name = team_data["name"]
        print(f"\n{'='*60}")
        print(f"正在处理 {team_name}")
        print("=" * 60)
        
        team_results = {}
        
        for player_name, account_id in team_data["players"].items():
            current += 1
            print(f"\n[{current}/{total_players}] 正在获取 {player_name} (ID: {account_id}) 的数据...")
            
            # 获取玩家信息
            player_info = get_player_info(account_id)
            time.sleep(REQUEST_DELAY)
            
            # 获取比赛记录
            matches = get_player_matches(account_id, MATCHES_LIMIT)
            time.sleep(REQUEST_DELAY)
            
            if not matches:
                print(f"  ⚠️ 未能获取到比赛数据（可能是隐私设置问题）")
                team_results[player_name] = {
                    "account_id": account_id,
                    "error": "无法获取数据",
                    "profile": player_info.get('profile', {}) if player_info else {}
                }
                continue
            
            # 分析数据
            stats = analyze_matches(matches, hero_map)
            
            if stats:
                team_results[player_name] = {
                    "account_id": account_id,
                    "profile": player_info.get('profile', {}) if player_info else {},
                    "mmr_estimate": player_info.get('mmr_estimate', {}).get('estimate') if player_info else None,
                    "stats": stats
                }
                
                print(f"  ✅ 成功获取 {len(matches)} 场比赛数据")
                print(f"     胜率: {stats['win_rate']}% ({stats['wins']}胜/{stats['losses']}负)")
                print(f"     平均KDA: {stats['avg_kills']}/{stats['avg_deaths']}/{stats['avg_assists']} (比率: {stats['kda_ratio']})")
                print(f"     最常用英雄: {', '.join([h['hero'] for h in stats['top_heroes'][:3]])}")
            else:
                team_results[player_name] = {
                    "account_id": account_id,
                    "error": "数据分析失败"
                }
        
        all_results[team_name] = team_results
    
    return all_results, hero_map

def save_results(results, hero_map):
    """保存结果到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存JSON格式
    json_file = f"dota2_stats_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ JSON数据已保存到: {json_file}")
    
    # 保存CSV汇总
    csv_file = f"dota2_stats_{timestamp}.csv"
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "队伍", "玩家", "Account ID", "比赛场数", "胜场", "负场", "胜率%",
            "平均击杀", "平均死亡", "平均助攻", "KDA比率",
            "最常用英雄1", "场次1", "胜率1%",
            "最常用英雄2", "场次2", "胜率2%",
            "最常用英雄3", "场次3", "胜率3%"
        ])
        
        for team_name, team_data in results.items():
            for player_name, player_data in team_data.items():
                if "error" in player_data:
                    writer.writerow([team_name, player_name, player_data.get("account_id", ""), "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"])
                else:
                    stats = player_data["stats"]
                    top_heroes = stats.get("top_heroes", [])
                    
                    row = [
                        team_name, player_name, player_data["account_id"],
                        stats["total_matches"], stats["wins"], stats["losses"], stats["win_rate"],
                        stats["avg_kills"], stats["avg_deaths"], stats["avg_assists"], stats["kda_ratio"]
                    ]
                    
                    # 添加前3个常用英雄
                    for i in range(3):
                        if i < len(top_heroes):
                            hero = top_heroes[i]
                            row.extend([hero["hero"], hero["games"], hero["win_rate"]])
                        else:
                            row.extend(["", "", ""])
                    
                    writer.writerow(row)
    
    print(f"✅ CSV汇总已保存到: {csv_file}")
    
    # 保存详细的英雄使用报告
    report_file = f"dota2_hero_report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Dota 2 玩家英雄使用详细报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for team_name, team_data in results.items():
            f.write(f"\n{'='*60}\n")
            f.write(f"{team_name}\n")
            f.write(f"{'='*60}\n")
            
            for player_name, player_data in team_data.items():
                f.write(f"\n▶ {player_name} (ID: {player_data.get('account_id', 'N/A')})\n")
                f.write("-" * 40 + "\n")
                
                if "error" in player_data:
                    f.write(f"  ⚠️ {player_data['error']}\n")
                    continue
                
                stats = player_data["stats"]
                
                f.write(f"  总体数据:\n")
                f.write(f"    比赛场数: {stats['total_matches']}\n")
                f.write(f"    胜/负: {stats['wins']}/{stats['losses']} (胜率: {stats['win_rate']}%)\n")
                f.write(f"    平均KDA: {stats['avg_kills']}/{stats['avg_deaths']}/{stats['avg_assists']}\n")
                f.write(f"    KDA比率: {stats['kda_ratio']}\n")
                
                f.write(f"\n  常用英雄 (Top 10):\n")
                f.write(f"    {'英雄':<20} {'场次':<8} {'胜率':<10} {'平均KDA':<15}\n")
                f.write(f"    {'-'*53}\n")
                
                for hero in stats.get("top_heroes", []):
                    f.write(f"    {hero['hero']:<20} {hero['games']:<8} {hero['win_rate']:<10}% {hero['avg_kda']:<15}\n")
                
                f.write(f"\n  最近比赛:\n")
                for match in stats.get("recent_matches", []):
                    result = "✅胜" if match['won'] else "❌负"
                    f.write(f"    {match['start_time']} | {match['hero']:<15} | {match['kda']:<12} | {result} | {match['duration']}分钟\n")
                
                f.write("\n")
    
    print(f"✅ 详细报告已保存到: {report_file}")
    
    return json_file, csv_file, report_file

def generate_summary(results):
    """生成汇总统计"""
    print("\n" + "=" * 60)
    print("数据汇总")
    print("=" * 60)
    
    for team_name, team_data in results.items():
        print(f"\n📊 {team_name}")
        print("-" * 40)
        
        team_wins = 0
        team_losses = 0
        team_players = 0
        
        for player_name, player_data in team_data.items():
            if "error" not in player_data and "stats" in player_data:
                stats = player_data["stats"]
                team_wins += stats["wins"]
                team_losses += stats["losses"]
                team_players += 1
                
                top_hero = stats["top_heroes"][0] if stats["top_heroes"] else {"hero": "N/A", "games": 0}
                print(f"  {player_name}: {stats['win_rate']}%胜率, KDA {stats['kda_ratio']}, 招牌: {top_hero['hero']}({top_hero['games']}场)")
            else:
                print(f"  {player_name}: ⚠️ 数据缺失")
        
        if team_players > 0:
            team_win_rate = round(team_wins / (team_wins + team_losses) * 100, 2) if (team_wins + team_losses) > 0 else 0
            print(f"  ➡️ 队伍整体: {team_win_rate}%胜率 ({team_wins}胜/{team_losses}负)")

# ============== 入口 ==============

if __name__ == "__main__":
    try:
        # 获取数据
        results, hero_map = fetch_all_players_data()
        
        # 保存结果
        json_file, csv_file, report_file = save_results(results, hero_map)
        
        # 生成汇总
        generate_summary(results)
        
        print("\n" + "=" * 60)
        print("✅ 数据爬取完成!")
        print("=" * 60)
        print(f"生成的文件:")
        print(f"  - {json_file} (完整JSON数据)")
        print(f"  - {csv_file} (CSV汇总表格)")
        print(f"  - {report_file} (详细文本报告)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
