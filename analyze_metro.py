#!/usr/bin/env python3
"""
Analyze metro station data to find reversed station names on the same line.
Example: 河沙 ↔ 沙河 (both on Guangzhou Line 6)
"""

import json
import os
import glob
from collections import defaultdict

def reverse_chinese(s):
    """Reverse Chinese characters in a string."""
    return s[::-1]

def is_valid_reversal(name1, name2):
    """Check if two names are valid reversals of each other."""
    if len(name1) < 2 or len(name2) < 2:
        return False
    if name1 == name2:
        return False
    return reverse_chinese(name1) == name2

def parse_metro_file(filepath):
    """Parse a metro JSON file and extract line -> stations mapping."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return None, None

    if not isinstance(data, dict) or 'l' not in data:
        return None, None

    city_name = data.get('s', 'Unknown')
    lines = {}

    for line in data.get('l', []):
        line_name = line.get('ln', 'Unknown')
        stations = []
        for station in line.get('st', []):
            station_name = station.get('n', '')
            if station_name:
                stations.append(station_name)
        if stations:
            lines[line_name] = stations

    return city_name, lines

def find_reversed_pairs(lines):
    """Find all reversed station name pairs on the same line."""
    results = []

    for line_name, stations in lines.items():
        # Create a set for quick lookup
        station_set = set(stations)

        # Check each station for its reversal
        checked = set()
        for i, station in enumerate(stations):
            if station in checked:
                continue

            reversed_name = reverse_chinese(station)
            if reversed_name in station_set and reversed_name != station:
                # Found a pair!
                j = stations.index(reversed_name)
                results.append({
                    'line': line_name,
                    'station1': station,
                    'station1_pos': i + 1,
                    'station2': reversed_name,
                    'station2_pos': j + 1,
                })
                checked.add(station)
                checked.add(reversed_name)

    return results

def main():
    # Collect all metro files
    metro_files = []

    # Check different locations
    patterns = [
        '/tmp/metro_*.json',
        '/tmp/guangzhou_metro.json',
        '/tmp/shanghai_metro.json',
        '/tmp/shenzhen_metro.json',
    ]

    for pattern in patterns:
        metro_files.extend(glob.glob(pattern))

    # Also check the saved Beijing data
    beijing_file = '/root/.claude/projects/-v1-code-snomiao-sno-zhihu-tree-main/e9aa79a2-abd6-4bd5-a74a-0ca848c397b4/tool-results/toolu_012x7tQbQN3YJgcYgTrruxD9.txt'
    if os.path.exists(beijing_file):
        metro_files.append(beijing_file)

    metro_files = list(set(metro_files))  # Remove duplicates

    print("=" * 70)
    print("中国地铁站名字序颠倒分析 / Chinese Metro Reversed Station Names Analysis")
    print("=" * 70)
    print(f"\n分析 {len(metro_files)} 个城市的地铁数据...\n")

    all_results = []
    city_stats = {}

    for filepath in sorted(metro_files):
        city_name, lines = parse_metro_file(filepath)
        if city_name is None or lines is None:
            continue

        # Count stations
        total_stations = sum(len(s) for s in lines.values())
        city_stats[city_name] = {
            'lines': len(lines),
            'stations': total_stations
        }

        # Find reversed pairs
        pairs = find_reversed_pairs(lines)

        if pairs:
            for pair in pairs:
                pair['city'] = city_name
                all_results.append(pair)

    # Print statistics
    print("城市地铁数据统计 / City Metro Statistics:")
    print("-" * 50)
    for city, stats in sorted(city_stats.items()):
        print(f"  {city}: {stats['lines']}条线路, {stats['stations']}座车站")

    total_cities = len(city_stats)
    total_lines = sum(s['lines'] for s in city_stats.values())
    total_stations = sum(s['stations'] for s in city_stats.values())
    print("-" * 50)
    print(f"  总计: {total_cities}个城市, {total_lines}条线路, {total_stations}座车站")

    # Print results
    print("\n" + "=" * 70)
    print("发现的字序颠倒站名对 / Discovered Reversed Station Name Pairs")
    print("=" * 70)

    if all_results:
        for result in all_results:
            print(f"\n✓ 城市: {result['city']}")
            print(f"  线路: {result['line']}")
            print(f"  站名对: {result['station1']} (第{result['station1_pos']}站) ↔ {result['station2']} (第{result['station2_pos']}站)")
    else:
        print("\n未发现任何字序颠倒的站名对!")

    print(f"\n共发现 {len(all_results)} 对字序颠倒的站名")

    # Save results to JSON
    output_data = {
        'city_stats': city_stats,
        'reversed_pairs': all_results,
        'summary': {
            'total_cities': total_cities,
            'total_lines': total_lines,
            'total_stations': total_stations,
            'reversed_pairs_count': len(all_results)
        }
    }

    output_path = '/v1/code/snomiao/sno-zhihu/tree/main/tmp/metro_analysis_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {output_path}")

if __name__ == '__main__':
    main()
