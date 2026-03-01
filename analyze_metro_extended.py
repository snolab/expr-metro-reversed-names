#!/usr/bin/env python3
"""
Extended analysis: Find reversed station names across different lines,
and look for interesting patterns.
"""

import json
import os
import glob
from collections import defaultdict

def reverse_chinese(s):
    """Reverse Chinese characters in a string."""
    return s[::-1]

def parse_metro_file(filepath):
    """Parse a metro JSON file and extract city name and all stations by line."""
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

def find_cross_line_reversals(city_name, lines):
    """Find reversed pairs across different lines in the same city."""
    results = []

    # Build a map of all stations to their lines
    station_to_lines = defaultdict(list)
    for line_name, stations in lines.items():
        for i, station in enumerate(stations):
            station_to_lines[station].append((line_name, i + 1))

    # Check for reversals
    checked = set()
    for station in station_to_lines.keys():
        if station in checked:
            continue

        reversed_name = reverse_chinese(station)
        if reversed_name in station_to_lines and reversed_name != station:
            # Check if they're on different lines
            station_lines = set(l[0] for l in station_to_lines[station])
            reversed_lines = set(l[0] for l in station_to_lines[reversed_name])

            # If not on the same line, it's a cross-line reversal
            if not station_lines.intersection(reversed_lines):
                results.append({
                    'city': city_name,
                    'station1': station,
                    'station1_lines': list(station_lines),
                    'station2': reversed_name,
                    'station2_lines': list(reversed_lines),
                })
                checked.add(station)
                checked.add(reversed_name)

    return results

def find_partial_reversals(city_name, lines):
    """Find station names that partially reverse to another station (2+ char overlap)."""
    results = []

    all_stations = set()
    for stations in lines.values():
        all_stations.update(stations)

    # Look for interesting patterns
    checked = set()
    for station in all_stations:
        if len(station) < 2 or station in checked:
            continue

        # Check if any 2+ char substring reversed exists in another station
        for length in range(2, len(station) + 1):
            for start in range(len(station) - length + 1):
                substring = station[start:start + length]
                reversed_sub = reverse_chinese(substring)

                for other_station in all_stations:
                    if other_station != station and reversed_sub in other_station:
                        if length >= len(station) - 1:  # Significant overlap
                            results.append({
                                'city': city_name,
                                'station1': station,
                                'station2': other_station,
                                'pattern': f'{substring} ↔ {reversed_sub}',
                            })

    # Remove duplicates
    seen = set()
    unique_results = []
    for r in results:
        key = tuple(sorted([r['station1'], r['station2']]))
        if key not in seen:
            seen.add(key)
            unique_results.append(r)

    return unique_results

def find_interesting_patterns(city_name, lines):
    """Find other interesting station name patterns."""
    results = []

    all_stations = set()
    station_to_line = {}
    for line_name, stations in lines.items():
        for station in stations:
            all_stations.add(station)
            if station not in station_to_line:
                station_to_line[station] = []
            station_to_line[station].append(line_name)

    # Find palindrome station names (reads same forwards and backwards)
    for station in all_stations:
        if len(station) >= 2 and station == reverse_chinese(station):
            results.append({
                'city': city_name,
                'type': 'palindrome',
                'station': station,
                'lines': station_to_line[station],
            })

    # Find station pairs that differ by only one character swap
    station_list = list(all_stations)
    for i, s1 in enumerate(station_list):
        for s2 in station_list[i+1:]:
            if len(s1) == len(s2) == 2:
                if s1[0] == s2[1] and s1[1] == s2[0]:
                    # These are exact reversals, handled elsewhere
                    continue
            if len(s1) == len(s2) >= 3:
                # Check if they differ by swapping adjacent characters
                diff_positions = []
                for j, (c1, c2) in enumerate(zip(s1, s2)):
                    if c1 != c2:
                        diff_positions.append(j)
                if len(diff_positions) == 2 and diff_positions[1] - diff_positions[0] == 1:
                    # Adjacent characters swapped
                    if s1[diff_positions[0]] == s2[diff_positions[1]] and s1[diff_positions[1]] == s2[diff_positions[0]]:
                        results.append({
                            'city': city_name,
                            'type': 'adjacent_swap',
                            'station1': s1,
                            'station2': s2,
                            'lines1': station_to_line[s1],
                            'lines2': station_to_line[s2],
                        })

    return results

def main():
    # Collect all metro files
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

    metro_files = list(set(metro_files))

    print("=" * 70)
    print("扩展分析：跨线路字序颠倒与有趣模式")
    print("Extended Analysis: Cross-line Reversals and Interesting Patterns")
    print("=" * 70)

    cross_line_results = []
    interesting_results = []

    for filepath in sorted(metro_files):
        city_name, lines = parse_metro_file(filepath)
        if city_name is None or lines is None:
            continue

        # Find cross-line reversals
        cross_pairs = find_cross_line_reversals(city_name, lines)
        cross_line_results.extend(cross_pairs)

        # Find interesting patterns
        patterns = find_interesting_patterns(city_name, lines)
        interesting_results.extend(patterns)

    # Print cross-line reversals
    print("\n1. 跨线路字序颠倒站名对 / Cross-line Reversed Station Pairs")
    print("-" * 50)

    if cross_line_results:
        for result in cross_line_results:
            print(f"\n  城市: {result['city']}")
            print(f"    {result['station1']} ({', '.join(result['station1_lines'])}) ↔ {result['station2']} ({', '.join(result['station2_lines'])})")
        print(f"\n  共发现 {len(cross_line_results)} 对跨线路字序颠倒站名")
    else:
        print("\n  未发现跨线路字序颠倒站名对")

    # Print interesting patterns
    print("\n2. 有趣的站名模式 / Interesting Station Name Patterns")
    print("-" * 50)

    palindromes = [r for r in interesting_results if r['type'] == 'palindrome']
    swaps = [r for r in interesting_results if r['type'] == 'adjacent_swap']

    if palindromes:
        print("\n  回文站名 (读起来正反相同):")
        for p in palindromes[:10]:  # Limit output
            print(f"    {p['city']}: {p['station']} ({', '.join(p['lines'])})")

    if swaps:
        print("\n  相邻字符交换的站名对:")
        for s in swaps[:10]:  # Limit output
            print(f"    {s['city']}: {s['station1']} ↔ {s['station2']}")

    # Summary
    print("\n" + "=" * 70)
    print("总结 / Summary")
    print("=" * 70)
    print(f"跨线路字序颠倒站名对: {len(cross_line_results)}")
    print(f"回文站名: {len(palindromes)}")
    print(f"相邻字符交换站名对: {len(swaps)}")

    # Save extended results
    output_data = {
        'cross_line_reversals': cross_line_results,
        'palindromes': palindromes,
        'adjacent_swaps': swaps,
    }

    output_path = '/v1/code/snomiao/sno-zhihu/tree/main/tmp/metro_extended_analysis.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {output_path}")

if __name__ == '__main__':
    main()
