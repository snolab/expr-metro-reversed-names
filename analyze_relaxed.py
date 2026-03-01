#!/usr/bin/env python3
"""
Relaxed Analysis: Find reversed station names with looser constraints
1. Cross-line reversals (different lines in same city)
2. Pinyin reversals (pinyin reads reversed)
3. Homophone matches (same pinyin, different characters)
"""

import json
import os
import glob
from collections import defaultdict
from pypinyin import pinyin, Style

def get_pinyin(text):
    """Get pinyin for Chinese text (without tones)."""
    py = pinyin(text, style=Style.NORMAL)
    return ''.join([p[0] for p in py])

def get_pinyin_with_tone(text):
    """Get pinyin with tone numbers."""
    py = pinyin(text, style=Style.TONE3)
    return ''.join([p[0] for p in py])

def reverse_string(s):
    """Reverse a string."""
    return s[::-1]

def reverse_pinyin_syllables(text):
    """Reverse pinyin syllables (not characters)."""
    py = pinyin(text, style=Style.NORMAL)
    syllables = [p[0] for p in py]
    return ''.join(reversed(syllables))

def parse_metro_file(filepath):
    """Parse a metro JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
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

def collect_all_data():
    """Collect data from all metro files."""
    metro_files = []
    patterns = [
        '/tmp/metro_*.json',
        '/tmp/guangzhou_metro.json',
        '/tmp/shanghai_metro.json',
        '/tmp/shenzhen_metro.json',
    ]
    for pattern in patterns:
        metro_files.extend(glob.glob(pattern))

    beijing_file = '/root/.claude/projects/-v1-code-snomiao-sno-zhihu-tree-main/e9aa79a2-abd6-4bd5-a74a-0ca848c397b4/tool-results/toolu_012x7tQbQN3YJgcYgTrruxD9.txt'
    if os.path.exists(beijing_file):
        metro_files.append(beijing_file)

    return list(set(metro_files))

def analyze_cross_line_reversals(city_name, lines):
    """Find character-reversed pairs across different lines."""
    results = []

    # Build station to line mapping
    station_to_lines = defaultdict(set)
    for line_name, stations in lines.items():
        for station in stations:
            station_to_lines[station].add(line_name)

    all_stations = set(station_to_lines.keys())
    checked = set()

    for station in all_stations:
        if station in checked:
            continue
        reversed_name = reverse_string(station)
        if reversed_name in all_stations and reversed_name != station:
            # Check if on different lines
            lines1 = station_to_lines[station]
            lines2 = station_to_lines[reversed_name]

            results.append({
                'city': city_name,
                'type': 'cross_line_char_reversal',
                'station1': station,
                'station1_lines': list(lines1),
                'station2': reversed_name,
                'station2_lines': list(lines2),
                'same_line': bool(lines1 & lines2)
            })
            checked.add(station)
            checked.add(reversed_name)

    return results

def analyze_pinyin_reversals(city_name, lines):
    """Find pinyin-reversed pairs (syllables reversed)."""
    results = []

    # Build station to pinyin mapping
    all_stations = set()
    for stations in lines.values():
        all_stations.update(stations)

    station_pinyin = {}
    pinyin_to_stations = defaultdict(list)

    for station in all_stations:
        py = get_pinyin(station)
        station_pinyin[station] = py
        pinyin_to_stations[py].append(station)

    checked = set()

    for station in all_stations:
        if station in checked:
            continue

        py = station_pinyin[station]
        reversed_py = reverse_pinyin_syllables(station)

        # Find stations with reversed pinyin
        if reversed_py in pinyin_to_stations and reversed_py != py:
            for other_station in pinyin_to_stations[reversed_py]:
                if other_station != station:
                    results.append({
                        'city': city_name,
                        'type': 'pinyin_reversal',
                        'station1': station,
                        'pinyin1': py,
                        'station2': other_station,
                        'pinyin2': reversed_py,
                    })
                    checked.add(station)
                    checked.add(other_station)

    return results

def analyze_homophones(city_name, lines):
    """Find homophone pairs (same pinyin, different characters)."""
    results = []

    all_stations = set()
    for stations in lines.values():
        all_stations.update(stations)

    pinyin_to_stations = defaultdict(list)

    for station in all_stations:
        py = get_pinyin(station)
        pinyin_to_stations[py].append(station)

    # Find groups with multiple stations having same pinyin
    for py, stations in pinyin_to_stations.items():
        if len(stations) > 1:
            for i, s1 in enumerate(stations):
                for s2 in stations[i+1:]:
                    if s1 != s2:  # Different characters
                        results.append({
                            'city': city_name,
                            'type': 'homophone',
                            'station1': s1,
                            'station2': s2,
                            'pinyin': py,
                        })

    return results

def analyze_partial_pinyin_match(city_name, lines):
    """Find stations where pinyin partially matches in reverse."""
    results = []

    all_stations = set()
    station_to_lines = defaultdict(set)
    for line_name, stations in lines.items():
        for station in stations:
            all_stations.add(station)
            station_to_lines[station].add(line_name)

    # Get pinyin for all stations
    station_pinyin = {s: get_pinyin(s) for s in all_stations}

    # Check for interesting pinyin patterns
    checked = set()
    for s1 in all_stations:
        if s1 in checked:
            continue
        py1 = station_pinyin[s1]

        for s2 in all_stations:
            if s1 == s2 or s2 in checked:
                continue
            py2 = station_pinyin[s2]

            # Check if one pinyin is reverse of another
            if py1 == py2[::-1] and len(py1) >= 4:  # At least 2 syllables
                results.append({
                    'city': city_name,
                    'type': 'full_pinyin_reversal',
                    'station1': s1,
                    'pinyin1': py1,
                    'station2': s2,
                    'pinyin2': py2,
                    'lines1': list(station_to_lines[s1]),
                    'lines2': list(station_to_lines[s2]),
                })
                checked.add(s1)
                checked.add(s2)

    return results

def main():
    print("=" * 70)
    print("放宽约束分析 / Relaxed Constraint Analysis")
    print("=" * 70)

    metro_files = collect_all_data()
    print(f"\n分析 {len(metro_files)} 个城市的地铁数据...\n")

    all_cross_line = []
    all_pinyin_reversal = []
    all_homophones = []
    all_full_pinyin = []

    for filepath in sorted(metro_files):
        city_name, lines = parse_metro_file(filepath)
        if city_name is None:
            continue

        # Cross-line character reversals
        cross_line = analyze_cross_line_reversals(city_name, lines)
        all_cross_line.extend(cross_line)

        # Pinyin reversals
        pinyin_rev = analyze_pinyin_reversals(city_name, lines)
        all_pinyin_reversal.extend(pinyin_rev)

        # Full pinyin reversals
        full_pinyin = analyze_partial_pinyin_match(city_name, lines)
        all_full_pinyin.extend(full_pinyin)

        # Homophones (limit to avoid too many results)
        homophones = analyze_homophones(city_name, lines)
        all_homophones.extend(homophones[:10])  # Limit per city

    # Print results
    print("\n" + "=" * 70)
    print("1. 跨线路字序颠倒 / Cross-Line Character Reversals")
    print("=" * 70)

    same_line_pairs = [r for r in all_cross_line if r['same_line']]
    diff_line_pairs = [r for r in all_cross_line if not r['same_line']]

    print(f"\n同线路字序颠倒 (Same Line): {len(same_line_pairs)} 对")
    for r in same_line_pairs:
        print(f"  ✓ {r['city']}: {r['station1']} ↔ {r['station2']}")
        print(f"    线路: {', '.join(r['station1_lines'])}")

    print(f"\n跨线路字序颠倒 (Different Lines): {len(diff_line_pairs)} 对")
    for r in diff_line_pairs:
        print(f"  • {r['city']}: {r['station1']} ({', '.join(r['station1_lines'])}) ↔ {r['station2']} ({', '.join(r['station2_lines'])})")

    print("\n" + "=" * 70)
    print("2. 拼音完全颠倒 / Full Pinyin Reversal")
    print("=" * 70)

    print(f"\n发现 {len(all_full_pinyin)} 对拼音完全颠倒的站名:")
    for r in all_full_pinyin:
        print(f"  • {r['city']}: {r['station1']} ({r['pinyin1']}) ↔ {r['station2']} ({r['pinyin2']})")
        print(f"    线路: {', '.join(r['lines1'])} / {', '.join(r['lines2'])}")

    print("\n" + "=" * 70)
    print("3. 同音不同字 / Homophones (部分展示)")
    print("=" * 70)

    print(f"\n发现 {len(all_homophones)} 对同音站名 (展示前20对):")
    for r in all_homophones[:20]:
        print(f"  • {r['city']}: {r['station1']} = {r['station2']} (pinyin: {r['pinyin']})")

    # Summary
    print("\n" + "=" * 70)
    print("总结 / Summary")
    print("=" * 70)
    print(f"同线路字序颠倒: {len(same_line_pairs)} 对")
    print(f"跨线路字序颠倒: {len(diff_line_pairs)} 对")
    print(f"拼音完全颠倒: {len(all_full_pinyin)} 对")
    print(f"同音不同字: {len(all_homophones)} 对")

    # Save results
    output = {
        'same_line_reversals': same_line_pairs,
        'cross_line_reversals': diff_line_pairs,
        'pinyin_reversals': all_full_pinyin,
        'homophones': all_homophones,
    }

    output_path = '/v1/code/snomiao/sno-zhihu/tree/main/tmp/relaxed_analysis_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {output_path}")

if __name__ == '__main__':
    main()
