"""
Dota 2 玩家数据分析工具 - 增强版
用于赛前对手分析，包含位置分析、状态趋势、对局时长分析
"""

import requests
import time
import json
from collections import defaultdict
from datetime import datetime
import csv
import os

# ============== 配置区域 ==============

# 队伍和玩家数据
TEAMS = {
    1: {
        "name": "队伍1",
        "color": "#FFF2CC",
        "players": {
            "思Kirara": 149901486,
            "德德": 216565503,
            "awe": 1101454493,
            "peter": 148670526,
            "JY.LIU": 364671117,
        }
    },
    2: {
        "name": "队伍2",
        "color": "#D5E8D4",
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
        "color": "#DAE8FC",
        "players": {
            "LiffyIsland": 301128180,
            "Ym": 138637714,
            "海柱哥": 160800934,
            "walker": 174245541,
        }
    },
    4: {
        "name": "队伍4",
        "color": "#E1D5E7",
        "players": {
            "黄神AME": 225835718,
            "邮寄时光": 354739911,
            "看我干嘛": 136320131,
            "yuan.": 365587496,
        }
    },
    5: {
        "name": "队伍5",
        "color": "#FFE6CC",
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
        "color": "#F8CECC",
        "players": {
            "彭律": 146348911,
            "世涛": 140976240,
            "Destiny": 86788193,
        }
    },
    7: {
        "name": "队伍7",
        "color": "#B4A7D6",
        "players": {
            "水豚噜噜": 900466924,
            "含章可贞": 387262791,
            "CatU": 157428753,
            "六柒柒": 847434740,
        }
    },
    8: {
        "name": "队伍8",
        "color": "#A9D08E",
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
REQUEST_DELAY = 1.5
MATCHES_LIMIT = 100

# 位置分析 - 英雄角色映射
# 1=Carry, 2=Mid, 3=Offlane, 4=Soft Support, 5=Hard Support
HERO_POSITIONS = {
    # Carry (1号位)
    "Anti-Mage": 1, "Phantom Assassin": 1, "Juggernaut": 1, "Slark": 1,
    "Faceless Void": 1, "Spectre": 1, "Terrorblade": 1, "Morphling": 1,
    "Phantom Lancer": 1, "Naga Siren": 1, "Medusa": 1, "Luna": 1,
    "Gyrocopter": 1, "Lifestealer": 1, "Ursa": 1, "Troll Warlord": 1,
    "Wraith King": 1, "Chaos Knight": 1, "Sven": 1, "Drow Ranger": 1,
    "Bloodseeker": 1, "Riki": 1, "Sniper": 1, "Weaver": 1, "Clinkz": 1,
    "Monkey King": 1, "Muerta": 1, "Arc Warden": 1, "Lone Druid": 1,

    # Mid (2号位)
    "Shadow Fiend": 2, "Storm Spirit": 2, "Queen of Pain": 2, "Invoker": 2,
    "Templar Assassin": 2, "Ember Spirit": 2, "Tinker": 2, "Lina": 2,
    "Outworld Destroyer": 2, "Puck": 2, "Void Spirit": 2, "Zeus": 2,
    "Huskar": 2, "Kunkka": 2, "Leshrac": 2, "Death Prophet": 2,
    "Viper": 2, "Razor": 2, "Necrophos": 2, "Windranger": 2,
    "Meepo": 2, "Broodmother": 2, "Pangolier": 2, "Hoodwink": 2,

    # Offlane (3号位)
    "Axe": 3, "Legion Commander": 3, "Centaur Warrunner": 3, "Tidehunter": 3,
    "Mars": 3, "Underlord": 3, "Bristleback": 3, "Timbersaw": 3,
    "Beastmaster": 3, "Dark Seer": 3, "Enigma": 3, "Magnus": 3,
    "Sand King": 3, "Slardar": 3, "Spirit Breaker": 3, "Clockwerk": 3,
    "Night Stalker": 3, "Doom": 3, "Brewmaster": 3, "Elder Titan": 3,
    "Primal Beast": 3, "Marci": 3, "Dawn Breaker": 3, "Dragon Knight": 3,
    "Batrider": 3, "Earth Spirit": 3, "Phoenix": 3,

    # Soft Support (4号位)
    "Earthshaker": 4, "Tusk": 4, "Earth Spirit": 4, "Mirana": 4,
    "Rubick": 4, "Tiny": 4, "Nyx Assassin": 4, "Pudge": 4,
    "Bounty Hunter": 4, "Techies": 4, "Snapfire": 4, "Grimstroke": 4,
    "Hoodwink": 4, "Dark Willow": 4, "Treant Protector": 4,

    # Hard Support (5号位)
    "Crystal Maiden": 5, "Lion": 5, "Shadow Shaman": 5, "Witch Doctor": 5,
    "Lich": 5, "Dazzle": 5, "Oracle": 5, "Io": 5, "Chen": 5,
    "Enchantress": 5, "Keeper of the Light": 5, "Shadow Demon": 5,
    "Bane": 5, "Disruptor": 5, "Ancient Apparition": 5, "Vengeful Spirit": 5,
    "Ogre Magi": 5, "Jakiro": 5, "Warlock": 5, "Winter Wyvern": 5,
    "Silencer": 5, "Skywrath Mage": 5, "Undying": 5, "Abaddon": 5,
}

POSITION_NAMES = {
    1: "C位/1号位",
    2: "中单/2号位",
    3: "三号位",
    4: "4号位辅助",
    5: "5号位辅助",
    0: "未知位置"
}

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

# ============== 位置分析 ==============

def analyze_position(hero_usage):
    """基于英雄使用情况推断玩家位置"""
    position_games = defaultdict(int)
    position_heroes = defaultdict(list)

    for hero_name, stats in hero_usage.items():
        games = stats["games"]
        pos = HERO_POSITIONS.get(hero_name, 0)
        if pos > 0:
            position_games[pos] += games
            position_heroes[pos].append({
                "hero": hero_name,
                "games": games,
                "wins": stats["wins"],
                "win_rate": round(stats["wins"] / games * 100, 1) if games > 0 else 0
            })

    # 找出最常玩的位置
    if position_games:
        main_position = max(position_games, key=position_games.get)
        total_identified = sum(position_games.values())
        confidence = round(position_games[main_position] / total_identified * 100, 1) if total_identified > 0 else 0
    else:
        main_position = 0
        confidence = 0

    # 对每个位置的英雄按使用次数排序
    for pos in position_heroes:
        position_heroes[pos] = sorted(position_heroes[pos], key=lambda x: x["games"], reverse=True)

    return {
        "main_position": main_position,
        "position_name": POSITION_NAMES.get(main_position, "未知"),
        "confidence": confidence,
        "position_distribution": dict(position_games),
        "heroes_by_position": dict(position_heroes)
    }

# ============== 状态趋势分析 ==============

def analyze_trend(matches, hero_map):
    """分析近期状态趋势 (最近20场 vs 前80场)"""
    if len(matches) < 20:
        return None

    recent_matches = matches[:20]
    older_matches = matches[20:] if len(matches) > 20 else []

    def calc_stats(match_list):
        if not match_list:
            return None
        wins = 0
        total_kills = 0
        total_deaths = 0
        total_assists = 0

        for match in match_list:
            player_slot = match.get('player_slot', 0)
            radiant_win = match.get('radiant_win', False)
            is_radiant = player_slot < 128
            won = (is_radiant and radiant_win) or (not is_radiant and not radiant_win)
            if won:
                wins += 1

            total_kills += match.get('kills', 0) or 0
            total_deaths += match.get('deaths', 0) or 0
            total_assists += match.get('assists', 0) or 0

        count = len(match_list)
        kda = round((total_kills + total_assists) / max(total_deaths, 1), 2)
        return {
            "games": count,
            "wins": wins,
            "win_rate": round(wins / count * 100, 1),
            "avg_kills": round(total_kills / count, 1),
            "avg_deaths": round(total_deaths / count, 1),
            "avg_assists": round(total_assists / count, 1),
            "kda": kda
        }

    recent_stats = calc_stats(recent_matches)
    older_stats = calc_stats(older_matches) if older_matches else None

    # 计算趋势
    trend = {
        "recent": recent_stats,
        "older": older_stats,
        "trend_direction": "stable"
    }

    if older_stats:
        win_rate_diff = recent_stats["win_rate"] - older_stats["win_rate"]
        kda_diff = recent_stats["kda"] - older_stats["kda"]

        trend["win_rate_change"] = round(win_rate_diff, 1)
        trend["kda_change"] = round(kda_diff, 2)

        # 判断趋势方向
        if win_rate_diff > 5 and kda_diff > 0.3:
            trend["trend_direction"] = "up"
            trend["trend_emoji"] = "🔥"
            trend["trend_text"] = "状态上升"
        elif win_rate_diff < -5 and kda_diff < -0.3:
            trend["trend_direction"] = "down"
            trend["trend_emoji"] = "📉"
            trend["trend_text"] = "状态下滑"
        else:
            trend["trend_direction"] = "stable"
            trend["trend_emoji"] = "➡️"
            trend["trend_text"] = "状态稳定"

    return trend

# ============== 对局时长分析 ==============

def analyze_game_duration(matches, hero_map):
    """分析不同时长对局的表现"""
    duration_stats = {
        "early": {"games": 0, "wins": 0, "kills": 0, "deaths": 0, "assists": 0},  # <30分钟
        "mid": {"games": 0, "wins": 0, "kills": 0, "deaths": 0, "assists": 0},    # 30-45分钟
        "late": {"games": 0, "wins": 0, "kills": 0, "deaths": 0, "assists": 0}    # >45分钟
    }

    for match in matches:
        duration = match.get('duration', 0) / 60  # 转换为分钟

        if duration < 30:
            category = "early"
        elif duration <= 45:
            category = "mid"
        else:
            category = "late"

        player_slot = match.get('player_slot', 0)
        radiant_win = match.get('radiant_win', False)
        is_radiant = player_slot < 128
        won = (is_radiant and radiant_win) or (not is_radiant and not radiant_win)

        duration_stats[category]["games"] += 1
        if won:
            duration_stats[category]["wins"] += 1
        duration_stats[category]["kills"] += match.get('kills', 0) or 0
        duration_stats[category]["deaths"] += match.get('deaths', 0) or 0
        duration_stats[category]["assists"] += match.get('assists', 0) or 0

    # 计算各时段的统计数据
    result = {}
    labels = {
        "early": "早期(<30分钟)",
        "mid": "中期(30-45分钟)",
        "late": "后期(>45分钟)"
    }

    for period, stats in duration_stats.items():
        games = stats["games"]
        if games > 0:
            result[period] = {
                "label": labels[period],
                "games": games,
                "wins": stats["wins"],
                "win_rate": round(stats["wins"] / games * 100, 1),
                "kda": round((stats["kills"] + stats["assists"]) / max(stats["deaths"], 1), 2)
            }
        else:
            result[period] = {
                "label": labels[period],
                "games": 0,
                "wins": 0,
                "win_rate": 0,
                "kda": 0
            }

    # 找出最强时段
    best_period = max(result.keys(), key=lambda x: result[x]["win_rate"] if result[x]["games"] >= 5 else 0)
    result["best_period"] = best_period
    result["best_period_label"] = labels[best_period]

    return result

# ============== 综合数据分析 ==============

def analyze_matches(matches, hero_map):
    """分析比赛数据（增强版）"""
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
        "recent_matches": []
    }

    for match in matches:
        hero_id = match.get('hero_id', 0)
        hero_name = hero_map.get(hero_id, f"Unknown({hero_id})")

        player_slot = match.get('player_slot', 0)
        radiant_win = match.get('radiant_win', False)
        is_radiant = player_slot < 128
        won = (is_radiant and radiant_win) or (not is_radiant and not radiant_win)

        if won:
            stats["wins"] += 1
            stats["hero_usage"][hero_name]["wins"] += 1
        else:
            stats["losses"] += 1

        kills = match.get('kills', 0) or 0
        deaths = match.get('deaths', 0) or 0
        assists = match.get('assists', 0) or 0

        stats["total_kills"] += kills
        stats["total_deaths"] += deaths
        stats["total_assists"] += assists

        stats["hero_usage"][hero_name]["games"] += 1
        stats["hero_usage"][hero_name]["kills"] += kills
        stats["hero_usage"][hero_name]["deaths"] += deaths
        stats["hero_usage"][hero_name]["assists"] += assists

        if len(stats["recent_matches"]) < 10:
            stats["recent_matches"].append({
                "match_id": match.get('match_id'),
                "hero": hero_name,
                "kda": f"{kills}/{deaths}/{assists}",
                "won": won,
                "duration": match.get('duration', 0) // 60,
                "start_time": datetime.fromtimestamp(match.get('start_time', 0)).strftime('%Y-%m-%d %H:%M') if match.get('start_time') else "N/A"
            })

    # 计算基础统计
    total = stats["total_matches"]
    if total > 0:
        stats["avg_kills"] = round(stats["total_kills"] / total, 2)
        stats["avg_deaths"] = round(stats["total_deaths"] / total, 2)
        stats["avg_assists"] = round(stats["total_assists"] / total, 2)
        stats["win_rate"] = round(stats["wins"] / total * 100, 2)

        if stats["total_deaths"] > 0:
            stats["kda_ratio"] = round((stats["total_kills"] + stats["total_assists"]) / stats["total_deaths"], 2)
        else:
            stats["kda_ratio"] = stats["total_kills"] + stats["total_assists"]

    # 排序英雄
    sorted_heroes = sorted(stats["hero_usage"].items(), key=lambda x: x[1]["games"], reverse=True)
    stats["top_heroes"] = []
    for hero_name, hero_stats in sorted_heroes[:10]:
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

    # 新增分析
    stats["position_analysis"] = analyze_position(stats["hero_usage"])
    stats["trend_analysis"] = analyze_trend(matches, hero_map)
    stats["duration_analysis"] = analyze_game_duration(matches, hero_map)

    # 转换defaultdict为普通dict，确保JSON序列化正常
    stats["hero_usage"] = dict(stats["hero_usage"])

    return stats

# ============== 主程序 ==============

def fetch_all_players_data():
    """获取所有玩家数据"""
    print("=" * 60)
    print("Dota 2 玩家数据分析工具 - 增强版")
    print("=" * 60)

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

        team_results = {
            "color": team_data["color"],
            "players": {}
        }

        for player_name, account_id in team_data["players"].items():
            current += 1
            print(f"\n[{current}/{total_players}] 正在获取 {player_name} (ID: {account_id}) 的数据...")

            player_info = get_player_info(account_id)
            time.sleep(REQUEST_DELAY)

            matches = get_player_matches(account_id, MATCHES_LIMIT)
            time.sleep(REQUEST_DELAY)

            if not matches:
                print(f"  ⚠️ 未能获取到比赛数据")
                team_results["players"][player_name] = {
                    "account_id": account_id,
                    "error": "无法获取数据"
                }
                continue

            stats = analyze_matches(matches, hero_map)

            if stats:
                team_results["players"][player_name] = {
                    "account_id": account_id,
                    "profile": player_info.get('profile', {}) if player_info else {},
                    "stats": stats
                }

                pos = stats["position_analysis"]
                trend = stats.get("trend_analysis", {})
                trend_emoji = trend.get("trend_emoji", "➡️") if trend else "➡️"

                print(f"  ✅ 成功获取 {len(matches)} 场比赛数据")
                print(f"     位置: {pos['position_name']} (置信度: {pos['confidence']}%)")
                print(f"     胜率: {stats['win_rate']}% | KDA: {stats['kda_ratio']} {trend_emoji}")
                print(f"     招牌: {', '.join([h['hero'] for h in stats['top_heroes'][:3]])}")
            else:
                team_results["players"][player_name] = {
                    "account_id": account_id,
                    "error": "数据分析失败"
                }

        all_results[team_name] = team_results

    return all_results, hero_map

# ============== 报告生成 ==============

def generate_wechat_summary(results):
    """生成微信/飞书友好的文字摘要"""
    lines = []
    lines.append("=" * 40)
    lines.append("📊 Dota2 对手分析简报")
    lines.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 40)

    for team_name, team_data in results.items():
        lines.append(f"\n【{team_name}】")
        lines.append("-" * 30)

        for player_name, player_data in team_data.get("players", {}).items():
            if "error" in player_data:
                lines.append(f"❌ {player_name}: 数据缺失")
                continue

            stats = player_data["stats"]
            pos = stats["position_analysis"]
            trend = stats.get("trend_analysis", {})
            duration = stats.get("duration_analysis", {})

            trend_emoji = trend.get("trend_emoji", "➡️") if trend else "➡️"
            trend_text = trend.get("trend_text", "状态稳定") if trend else "状态稳定"

            # 主要信息行
            lines.append(f"\n🎯 {player_name} ({pos['position_name']}) {trend_emoji}{trend_text}")

            # 招牌英雄
            top3 = stats["top_heroes"][:3]
            hero_str = ", ".join([f"{h['hero']}({h['games']}场{h['win_rate']}%)" for h in top3])
            lines.append(f"   招牌: {hero_str}")

            # 整体数据
            lines.append(f"   整体: {stats['win_rate']}%胜率 KDA:{stats['kda_ratio']}")

            # 近期趋势
            if trend and trend.get("recent"):
                recent = trend["recent"]
                lines.append(f"   近20场: {recent['win_rate']}%胜率 KDA:{recent['kda']}")

            # 时段分析
            if duration:
                best = duration.get("best_period_label", "")
                best_data = duration.get(duration.get("best_period", ""), {})
                if best_data.get("games", 0) >= 5:
                    lines.append(f"   擅长: {best} ({best_data['win_rate']}%胜率)")

    lines.append("\n" + "=" * 40)

    return "\n".join(lines)

def generate_html_report(results, output_file):
    """生成HTML可视化报告"""
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dota2 对手分析报告</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 {
            text-align: center;
            padding: 30px;
            background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
        }
        .timestamp { text-align: center; color: #888; margin-bottom: 30px; }
        .team-section {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            margin: 20px 0;
            padding: 20px;
            border-left: 4px solid;
        }
        .team-title {
            font-size: 1.5em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .player-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
        .player-card {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s;
        }
        .player-card:hover { transform: translateY(-5px); }
        .player-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .player-name { font-size: 1.3em; font-weight: bold; }
        .player-position {
            background: rgba(255,255,255,0.1);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
        }
        .trend-up { color: #4ade80; }
        .trend-down { color: #f87171; }
        .trend-stable { color: #fbbf24; }
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .stat-label { color: #888; }
        .stat-value { font-weight: bold; }
        .hero-list { margin-top: 15px; }
        .hero-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            background: rgba(255,255,255,0.03);
            border-radius: 6px;
            margin: 5px 0;
        }
        .hero-name { font-weight: 500; }
        .hero-stats { color: #888; font-size: 0.9em; }
        .win-rate-bar {
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            margin-top: 5px;
            overflow: hidden;
        }
        .win-rate-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.5s;
        }
        .duration-analysis {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .duration-item {
            text-align: center;
            padding: 10px;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
        }
        .duration-label { font-size: 0.8em; color: #888; }
        .duration-value { font-size: 1.2em; font-weight: bold; margin-top: 5px; }
        .error-card {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Dota2 对手分析报告</h1>
        <p class="timestamp">生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
"""

    for team_name, team_data in results.items():
        color = team_data.get("color", "#666")
        html_content += f"""
        <div class="team-section" style="border-left-color: {color};">
            <h2 class="team-title">
                <span style="color: {color};">●</span> {team_name}
            </h2>
            <div class="player-cards">
"""

        for player_name, player_data in team_data.get("players", {}).items():
            if "error" in player_data:
                html_content += f"""
                <div class="player-card error-card">
                    <div class="player-header">
                        <span class="player-name">{player_name}</span>
                        <span class="player-position">❌ 数据缺失</span>
                    </div>
                    <p style="color: #f87171;">{player_data.get('error', '未知错误')}</p>
                </div>
"""
                continue

            stats = player_data["stats"]
            pos = stats["position_analysis"]
            trend = stats.get("trend_analysis", {})
            duration = stats.get("duration_analysis", {})

            trend_class = "trend-stable"
            trend_emoji = "➡️"
            trend_text = "稳定"
            if trend:
                if trend.get("trend_direction") == "up":
                    trend_class = "trend-up"
                    trend_emoji = "🔥"
                    trend_text = "上升"
                elif trend.get("trend_direction") == "down":
                    trend_class = "trend-down"
                    trend_emoji = "📉"
                    trend_text = "下滑"

            win_rate = stats['win_rate']
            win_rate_color = "#4ade80" if win_rate >= 55 else "#fbbf24" if win_rate >= 45 else "#f87171"

            html_content += f"""
                <div class="player-card">
                    <div class="player-header">
                        <span class="player-name">{player_name}</span>
                        <span class="player-position">{pos['position_name']}</span>
                    </div>

                    <div class="stat-row">
                        <span class="stat-label">整体胜率</span>
                        <span class="stat-value" style="color: {win_rate_color};">{win_rate}%</span>
                    </div>
                    <div class="win-rate-bar">
                        <div class="win-rate-fill" style="width: {win_rate}%; background: {win_rate_color};"></div>
                    </div>

                    <div class="stat-row">
                        <span class="stat-label">KDA比率</span>
                        <span class="stat-value">{stats['kda_ratio']}</span>
                    </div>

                    <div class="stat-row">
                        <span class="stat-label">近期状态</span>
                        <span class="stat-value {trend_class}">{trend_emoji} {trend_text}</span>
                    </div>
"""

            # 近期趋势详情
            if trend and trend.get("recent"):
                recent = trend["recent"]
                html_content += f"""
                    <div class="stat-row">
                        <span class="stat-label">近20场</span>
                        <span class="stat-value">{recent['win_rate']}% / KDA {recent['kda']}</span>
                    </div>
"""

            # 时长分析
            if duration:
                html_content += """
                    <div class="duration-analysis">
"""
                for period in ["early", "mid", "late"]:
                    d = duration.get(period, {})
                    if d.get("games", 0) > 0:
                        html_content += f"""
                        <div class="duration-item">
                            <div class="duration-label">{d.get('label', period)}</div>
                            <div class="duration-value">{d.get('win_rate', 0)}%</div>
                            <div class="duration-label">{d.get('games', 0)}场</div>
                        </div>
"""
                html_content += """
                    </div>
"""

            # 招牌英雄
            html_content += """
                    <div class="hero-list">
                        <div class="stat-label" style="margin-bottom: 10px;">招牌英雄</div>
"""
            for hero in stats["top_heroes"][:5]:
                hero_wr = hero['win_rate']
                hero_color = "#4ade80" if hero_wr >= 55 else "#fbbf24" if hero_wr >= 45 else "#f87171"
                html_content += f"""
                        <div class="hero-item">
                            <span class="hero-name">{hero['hero']}</span>
                            <span class="hero-stats">{hero['games']}场 <span style="color: {hero_color};">{hero_wr}%</span></span>
                        </div>
"""

            html_content += """
                    </div>
                </div>
"""

        html_content += """
            </div>
        </div>
"""

    html_content += """
    </div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_file

# ============== BP专用报告 ==============

# BP分析参数
BP_MIN_GAMES = 5       # 最少场次才算"擅长"
BP_HIGH_WINRATE = 55   # 高胜率阈值
BP_THREAT_WINRATE = 60 # 威胁级胜率阈值

def analyze_signature_heroes(player_stats):
    """
    分析选手的真正招牌英雄
    招牌英雄定义：场次>=5 且 胜率>=55%
    """
    signature_heroes = []
    comfort_heroes = []  # 熟练但胜率一般

    for hero in player_stats.get("top_heroes", []):
        games = hero["games"]
        win_rate = hero["win_rate"]

        if games >= BP_MIN_GAMES:
            if win_rate >= BP_HIGH_WINRATE:
                signature_heroes.append({
                    **hero,
                    "threat_level": "high" if win_rate >= BP_THREAT_WINRATE else "medium"
                })
            elif win_rate >= 45:
                comfort_heroes.append(hero)

    return {
        "signature": signature_heroes,  # 真正的招牌（必Ban候选）
        "comfort": comfort_heroes,       # 熟练英雄（次优先）
        "pool_depth": len(signature_heroes),
        "is_shallow_pool": len(signature_heroes) <= 2  # 英雄池浅
    }

def calculate_ban_priority(hero, player_name, position):
    """计算英雄的Ban优先级分数"""
    games = hero["games"]
    win_rate = hero["win_rate"]

    # 基础分 = 胜率
    score = win_rate

    # 场次加成（场次越多越稳定）
    if games >= 15:
        score += 10
    elif games >= 10:
        score += 5

    # 高胜率额外加成
    if win_rate >= 70:
        score += 15
    elif win_rate >= 60:
        score += 8

    return {
        "hero": hero["hero"],
        "player": player_name,
        "position": position,
        "games": games,
        "win_rate": win_rate,
        "priority_score": round(score, 1)
    }

def generate_bp_report(results, output_file):
    """生成BP专用报告"""
    lines = []

    lines.append("=" * 70)
    lines.append("🎯 DOTA2 BP专用分析报告")
    lines.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)
    lines.append("")
    lines.append("【报告说明】")
    lines.append(f"  • 招牌英雄: 场次≥{BP_MIN_GAMES} 且 胜率≥{BP_HIGH_WINRATE}%")
    lines.append(f"  • 威胁级别: 胜率≥{BP_THREAT_WINRATE}%为高威胁(🔴)，≥{BP_HIGH_WINRATE}%为中威胁(🟡)")
    lines.append("  • 英雄池浅: 招牌英雄≤2个，容易被针对")
    lines.append("")

    # 收集所有Ban建议
    all_ban_suggestions = []

    for team_name, team_data in results.items():
        lines.append("")
        lines.append("=" * 70)
        lines.append(f"【{team_name}】")
        lines.append("=" * 70)

        team_ban_suggestions = []
        team_hero_pool = {}  # 队伍英雄池汇总

        for player_name, player_data in team_data.get("players", {}).items():
            if "error" in player_data:
                lines.append(f"\n❌ {player_name}: 数据缺失，无法分析")
                continue

            stats = player_data["stats"]
            pos = stats["position_analysis"]
            position_name = pos["position_name"]
            trend = stats.get("trend_analysis", {})

            # 分析招牌英雄
            hero_analysis = analyze_signature_heroes(stats)
            signature = hero_analysis["signature"]
            comfort = hero_analysis["comfort"]

            # 状态标记
            trend_emoji = ""
            if trend:
                if trend.get("trend_direction") == "up":
                    trend_emoji = " 🔥状态火热"
                elif trend.get("trend_direction") == "down":
                    trend_emoji = " 📉状态低迷"

            lines.append("")
            lines.append(f"┌─────────────────────────────────────────")
            lines.append(f"│ 🎮 {player_name} [{position_name}]{trend_emoji}")
            lines.append(f"│    整体: {stats['win_rate']}%胜率 | KDA: {stats['kda_ratio']}")

            if trend and trend.get("recent"):
                recent = trend["recent"]
                lines.append(f"│    近20场: {recent['win_rate']}%胜率 | KDA: {recent['kda']}")

            lines.append(f"├─────────────────────────────────────────")

            # 招牌英雄（必Ban候选）
            if signature:
                lines.append(f"│ 🚨 必Ban候选 ({len(signature)}个):")
                for hero in signature:
                    threat = "🔴" if hero["threat_level"] == "high" else "🟡"
                    lines.append(f"│    {threat} {hero['hero']}: {hero['games']}场 {hero['win_rate']}%胜率")

                    # 加入Ban建议
                    ban_item = calculate_ban_priority(hero, player_name, position_name)
                    team_ban_suggestions.append(ban_item)
                    all_ban_suggestions.append({**ban_item, "team": team_name})

                    # 加入队伍英雄池
                    hero_name = hero["hero"]
                    if hero_name not in team_hero_pool:
                        team_hero_pool[hero_name] = []
                    team_hero_pool[hero_name].append({
                        "player": player_name,
                        "position": position_name,
                        "games": hero["games"],
                        "win_rate": hero["win_rate"]
                    })
            else:
                lines.append(f"│ ⚪ 无明显招牌英雄")

            # 熟练英雄
            if comfort:
                lines.append(f"│ 📋 熟练英雄:")
                comfort_str = ", ".join([f"{h['hero']}({h['games']}场{h['win_rate']}%)" for h in comfort[:4]])
                lines.append(f"│    {comfort_str}")

            # 英雄池评估
            if hero_analysis["is_shallow_pool"]:
                lines.append(f"│ ⚠️ 英雄池较浅! 只有{hero_analysis['pool_depth']}个招牌英雄")
                lines.append(f"│    → Ban掉招牌后可能影响发挥")

            lines.append(f"└─────────────────────────────────────────")

        # 队伍Ban建议汇总
        if team_ban_suggestions:
            lines.append("")
            lines.append(f"📊 {team_name} Ban优先级排序:")
            lines.append("-" * 50)
            team_ban_suggestions.sort(key=lambda x: x["priority_score"], reverse=True)
            for i, ban in enumerate(team_ban_suggestions[:8], 1):
                lines.append(f"  {i}. {ban['hero']} ({ban['player']}) - {ban['games']}场{ban['win_rate']}% [分数:{ban['priority_score']}]")

        # 队伍英雄池汇总
        if team_hero_pool:
            lines.append("")
            lines.append(f"📋 {team_name} 核心英雄池:")
            lines.append("-" * 50)
            # 按使用人数排序
            sorted_pool = sorted(team_hero_pool.items(), key=lambda x: len(x[1]), reverse=True)
            for hero_name, players in sorted_pool[:10]:
                if len(players) > 1:
                    player_str = ", ".join([f"{p['player']}({p['win_rate']}%)" for p in players])
                    lines.append(f"  🔸 {hero_name}: {player_str}")
                else:
                    p = players[0]
                    lines.append(f"  • {hero_name}: {p['player']} ({p['games']}场{p['win_rate']}%)")

    # 全局高威胁英雄汇总
    lines.append("")
    lines.append("=" * 70)
    lines.append("🏆 全局高威胁英雄榜 (所有队伍)")
    lines.append("=" * 70)

    all_ban_suggestions.sort(key=lambda x: x["priority_score"], reverse=True)
    for i, ban in enumerate(all_ban_suggestions[:15], 1):
        lines.append(f"  {i:2d}. {ban['hero']:<20} | {ban['player']:<12} | {ban['team']:<6} | {ban['games']}场 {ban['win_rate']}%")

    lines.append("")
    lines.append("=" * 70)
    lines.append("【BP建议使用方法】")
    lines.append("  1. 赛前查看对手队伍的'Ban优先级排序'")
    lines.append("  2. 优先Ban掉对方核心位置的高威胁英雄(🔴)")
    lines.append("  3. 关注'英雄池较浅'的选手，针对性Ban人")
    lines.append("  4. 如果多人共用英雄，一个Ban可以影响多人")
    lines.append("=" * 70)

    report_content = "\n".join(lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    return report_content

def generate_bp_html_report(results, output_file):
    """生成BP专用HTML报告"""
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dota2 BP分析报告</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f1a;
            color: #e0e0e0;
            padding: 20px;
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; color: #ff6b6b; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; }
        .legend {
            background: rgba(255,255,255,0.05);
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }
        .legend-item { display: flex; align-items: center; gap: 8px; }
        .dot { width: 12px; height: 12px; border-radius: 50%; }
        .dot-red { background: #ef4444; }
        .dot-yellow { background: #f59e0b; }
        .dot-gray { background: #6b7280; }
        .team-section {
            background: rgba(255,255,255,0.03);
            border-radius: 15px;
            margin: 25px 0;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .team-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .team-name { font-size: 1.5em; font-weight: bold; }
        .player-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
        .player-card {
            background: rgba(0,0,0,0.4);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .player-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        .player-name { font-size: 1.2em; font-weight: bold; color: #fff; }
        .player-position {
            background: rgba(99, 102, 241, 0.3);
            color: #a5b4fc;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
        }
        .player-stats { color: #888; font-size: 0.9em; margin-bottom: 15px; }
        .trend-hot { color: #f97316; }
        .trend-cold { color: #60a5fa; }
        .section-title {
            font-size: 0.85em;
            color: #888;
            margin: 15px 0 10px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .hero-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            margin: 6px 0;
            border-left: 3px solid transparent;
        }
        .hero-item.threat-high { border-left-color: #ef4444; background: rgba(239,68,68,0.1); }
        .hero-item.threat-medium { border-left-color: #f59e0b; background: rgba(245,158,11,0.1); }
        .hero-name { font-weight: 500; }
        .hero-stats-inline { font-size: 0.9em; color: #888; }
        .hero-winrate { font-weight: bold; }
        .winrate-high { color: #4ade80; }
        .winrate-mid { color: #fbbf24; }
        .winrate-low { color: #f87171; }
        .shallow-pool-warning {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 10px 15px;
            margin-top: 15px;
            font-size: 0.9em;
        }
        .ban-priority {
            background: rgba(99, 102, 241, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-top: 25px;
        }
        .ban-priority h3 { color: #a5b4fc; margin-bottom: 15px; }
        .ban-list { list-style: none; }
        .ban-list li {
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: space-between;
        }
        .ban-rank { color: #f59e0b; font-weight: bold; width: 30px; }
        .ban-hero { flex: 1; }
        .ban-player { color: #888; width: 100px; }
        .ban-score { color: #4ade80; width: 60px; text-align: right; }
        .no-signature { color: #666; font-style: italic; padding: 10px 0; }
    </style>
</head>
<body>
<div class="container">
    <h1>🎯 BP专用分析报告</h1>
    <p class="subtitle">""" + datetime.now().strftime('%Y-%m-%d %H:%M') + """ 生成</p>

    <div class="legend">
        <div class="legend-item"><span class="dot dot-red"></span> 高威胁 (胜率≥60%)</div>
        <div class="legend-item"><span class="dot dot-yellow"></span> 中威胁 (胜率≥55%)</div>
        <div class="legend-item"><span class="dot dot-gray"></span> 熟练英雄</div>
    </div>
"""

    for team_name, team_data in results.items():
        color = team_data.get("color", "#666")

        # 收集队伍Ban建议
        team_bans = []

        html += f"""
    <div class="team-section">
        <div class="team-header">
            <span class="team-name" style="color: {color};">● {team_name}</span>
        </div>
        <div class="player-grid">
"""

        for player_name, player_data in team_data.get("players", {}).items():
            if "error" in player_data:
                html += f"""
            <div class="player-card" style="opacity: 0.5;">
                <div class="player-header">
                    <span class="player-name">{player_name}</span>
                    <span class="player-position">数据缺失</span>
                </div>
            </div>
"""
                continue

            stats = player_data["stats"]
            pos = stats["position_analysis"]
            trend = stats.get("trend_analysis", {})

            hero_analysis = analyze_signature_heroes(stats)
            signature = hero_analysis["signature"]
            comfort = hero_analysis["comfort"]

            trend_html = ""
            if trend:
                if trend.get("trend_direction") == "up":
                    trend_html = '<span class="trend-hot">🔥 状态火热</span>'
                elif trend.get("trend_direction") == "down":
                    trend_html = '<span class="trend-cold">📉 状态低迷</span>'

            html += f"""
            <div class="player-card">
                <div class="player-header">
                    <div>
                        <div class="player-name">{player_name}</div>
                        <div class="player-stats">{stats['win_rate']}%胜率 | KDA {stats['kda_ratio']} {trend_html}</div>
                    </div>
                    <span class="player-position">{pos['position_name']}</span>
                </div>
"""

            if signature:
                html += '<div class="section-title">🚨 必Ban候选</div>'
                for hero in signature:
                    threat_class = "threat-high" if hero["threat_level"] == "high" else "threat-medium"
                    wr_class = "winrate-high" if hero["win_rate"] >= 60 else "winrate-mid"
                    html += f"""
                <div class="hero-item {threat_class}">
                    <span class="hero-name">{hero['hero']}</span>
                    <span class="hero-stats-inline">{hero['games']}场 <span class="hero-winrate {wr_class}">{hero['win_rate']}%</span></span>
                </div>
"""
                    # 添加到队伍Ban列表
                    ban_item = calculate_ban_priority(hero, player_name, pos['position_name'])
                    team_bans.append(ban_item)
            else:
                html += '<div class="no-signature">无明显招牌英雄</div>'

            if comfort:
                html += '<div class="section-title">熟练英雄</div>'
                for hero in comfort[:3]:
                    wr_class = "winrate-mid" if hero["win_rate"] >= 50 else "winrate-low"
                    html += f"""
                <div class="hero-item">
                    <span class="hero-name">{hero['hero']}</span>
                    <span class="hero-stats-inline">{hero['games']}场 <span class="hero-winrate {wr_class}">{hero['win_rate']}%</span></span>
                </div>
"""

            if hero_analysis["is_shallow_pool"]:
                html += f"""
                <div class="shallow-pool-warning">
                    ⚠️ 英雄池较浅 (仅{hero_analysis['pool_depth']}个招牌) - 容易被针对
                </div>
"""

            html += "</div>"

        html += "</div>"  # player-grid

        # 队伍Ban优先级
        if team_bans:
            team_bans.sort(key=lambda x: x["priority_score"], reverse=True)
            html += """
        <div class="ban-priority">
            <h3>📊 Ban优先级排序</h3>
            <ul class="ban-list">
"""
            for i, ban in enumerate(team_bans[:8], 1):
                html += f"""
                <li>
                    <span class="ban-rank">{i}.</span>
                    <span class="ban-hero">{ban['hero']}</span>
                    <span class="ban-player">{ban['player']}</span>
                    <span class="ban-score">{ban['games']}场 {ban['win_rate']}%</span>
                </li>
"""
            html += """
            </ul>
        </div>
"""

        html += "</div>"  # team-section

    html += """
</div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_file

def generate_bp_markdown_report(results, output_file):
    """生成BP专用Markdown报告（适合上传腾讯文档）"""
    lines = []

    lines.append("# Dota2 BP分析报告")
    lines.append("")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## 报告说明")
    lines.append("")
    lines.append(f"- **招牌英雄**: 场次≥{BP_MIN_GAMES} 且 胜率≥{BP_HIGH_WINRATE}%")
    lines.append(f"- **高威胁** 🔴: 胜率≥{BP_THREAT_WINRATE}%")
    lines.append(f"- **中威胁** 🟡: 胜率≥{BP_HIGH_WINRATE}%")
    lines.append("- **英雄池浅**: 招牌英雄≤2个，容易被针对")
    lines.append("")

    # 收集所有Ban建议
    all_ban_suggestions = []

    for team_name, team_data in results.items():
        lines.append("---")
        lines.append("")
        lines.append(f"## {team_name}")
        lines.append("")

        team_ban_suggestions = []

        for player_name, player_data in team_data.get("players", {}).items():
            if "error" in player_data:
                lines.append(f"### ❌ {player_name}")
                lines.append("")
                lines.append("数据缺失，无法分析")
                lines.append("")
                continue

            stats = player_data["stats"]
            pos = stats["position_analysis"]
            position_name = pos["position_name"]
            trend = stats.get("trend_analysis", {})

            hero_analysis = analyze_signature_heroes(stats)
            signature = hero_analysis["signature"]
            comfort = hero_analysis["comfort"]

            # 状态标记
            trend_text = ""
            if trend:
                if trend.get("trend_direction") == "up":
                    trend_text = " 🔥状态火热"
                elif trend.get("trend_direction") == "down":
                    trend_text = " 📉状态低迷"

            lines.append(f"### {player_name} 【{position_name}】{trend_text}")
            lines.append("")

            # 基础数据
            lines.append(f"**整体**: {stats['win_rate']}%胜率 | KDA: {stats['kda_ratio']}")
            if trend and trend.get("recent"):
                recent = trend["recent"]
                lines.append(f"**近20场**: {recent['win_rate']}%胜率 | KDA: {recent['kda']}")
            lines.append("")

            # 招牌英雄表格
            if signature:
                lines.append("#### 🚨 必Ban候选")
                lines.append("")
                lines.append("| 英雄 | 场次 | 胜率 | 威胁 |")
                lines.append("|------|------|------|------|")
                for hero in signature:
                    threat = "🔴高" if hero["threat_level"] == "high" else "🟡中"
                    lines.append(f"| {hero['hero']} | {hero['games']} | {hero['win_rate']}% | {threat} |")

                    ban_item = calculate_ban_priority(hero, player_name, position_name)
                    team_ban_suggestions.append(ban_item)
                    all_ban_suggestions.append({**ban_item, "team": team_name})
                lines.append("")
            else:
                lines.append("*无明显招牌英雄*")
                lines.append("")

            # 熟练英雄
            if comfort:
                comfort_str = ", ".join([f"{h['hero']}({h['games']}场{h['win_rate']}%)" for h in comfort[:4]])
                lines.append(f"**熟练英雄**: {comfort_str}")
                lines.append("")

            # 英雄池评估
            if hero_analysis["is_shallow_pool"]:
                lines.append(f"> ⚠️ **英雄池较浅**（仅{hero_analysis['pool_depth']}个招牌）- Ban掉后可能影响发挥")
                lines.append("")

        # 队伍Ban建议
        if team_ban_suggestions:
            lines.append(f"### 📊 {team_name} Ban优先级")
            lines.append("")
            lines.append("| 排名 | 英雄 | 选手 | 场次 | 胜率 |")
            lines.append("|------|------|------|------|------|")
            team_ban_suggestions.sort(key=lambda x: x["priority_score"], reverse=True)
            for i, ban in enumerate(team_ban_suggestions[:8], 1):
                lines.append(f"| {i} | {ban['hero']} | {ban['player']} | {ban['games']} | {ban['win_rate']}% |")
            lines.append("")

    # 全局高威胁英雄榜
    lines.append("---")
    lines.append("")
    lines.append("## 🏆 全局高威胁英雄榜")
    lines.append("")
    lines.append("| 排名 | 英雄 | 选手 | 队伍 | 场次 | 胜率 |")
    lines.append("|------|------|------|------|------|------|")

    all_ban_suggestions.sort(key=lambda x: x["priority_score"], reverse=True)
    for i, ban in enumerate(all_ban_suggestions[:15], 1):
        lines.append(f"| {i} | {ban['hero']} | {ban['player']} | {ban['team']} | {ban['games']} | {ban['win_rate']}% |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## BP建议")
    lines.append("")
    lines.append("1. 赛前查看对手队伍的「Ban优先级」表格")
    lines.append("2. 优先Ban掉对方核心位置的高威胁英雄（🔴）")
    lines.append("3. 关注「英雄池较浅」的选手，2-3个Ban可能卡死")
    lines.append("4. 如果队伍多人共用某英雄，一个Ban影响多人")
    lines.append("")

    report_content = "\n".join(lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    return output_file

def save_results(results, hero_map):
    """保存所有结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # 1. 保存JSON
    json_file = f"{output_dir}/dota2_analysis_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        # 转换 defaultdict 为普通 dict
        def convert_dict(obj):
            if isinstance(obj, defaultdict):
                return dict(obj)
            return obj
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✅ JSON数据: {json_file}")

    # 2. 生成HTML报告
    html_file = f"{output_dir}/dota2_report_{timestamp}.html"
    generate_html_report(results, html_file)
    print(f"✅ HTML报告: {html_file}")

    # 3. 生成微信摘要
    summary = generate_wechat_summary(results)
    summary_file = f"{output_dir}/dota2_summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"✅ 微信摘要: {summary_file}")

    # 4. 生成BP专用报告
    bp_txt_file = f"{output_dir}/bp_report_{timestamp}.txt"
    bp_report = generate_bp_report(results, bp_txt_file)
    print(f"✅ BP报告(TXT): {bp_txt_file}")

    # 5. 生成BP专用HTML报告
    bp_html_file = f"{output_dir}/bp_report_{timestamp}.html"
    generate_bp_html_report(results, bp_html_file)
    print(f"✅ BP报告(HTML): {bp_html_file}")

    # 6. 生成BP专用Markdown报告（腾讯文档友好）
    bp_md_file = f"{output_dir}/bp_report_{timestamp}.md"
    generate_bp_markdown_report(results, bp_md_file)
    print(f"✅ BP报告(MD): {bp_md_file}")

    # 7. 打印BP报告到控制台
    print("\n" + "=" * 60)
    print("BP专用报告")
    print("=" * 60)
    print(bp_report)

    return json_file, html_file, summary_file, bp_txt_file, bp_html_file, bp_md_file

# ============== 入口 ==============

if __name__ == "__main__":
    try:
        results, hero_map = fetch_all_players_data()
        files = save_results(results, hero_map)

        print("\n" + "=" * 60)
        print("✅ 数据分析完成!")
        print("=" * 60)
        print(f"生成的文件:")
        for f in files:
            print(f"  - {f}")

        print("\n💡 提示: 打开 bp_report_*.html 查看BP专用分析报告")

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
