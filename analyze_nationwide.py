#!/usr/bin/env python3
"""
Analyze reversed metro station names across the entire country.
Find all pairs where station A in any city has a reversed name matching station B in any city.
"""

import json
import urllib.request
from collections import defaultdict

CITIES = {
    "1100": "beijing", "3100": "shanghai", "4401": "guangzhou", "4403": "shenzhen",
    "5000": "chongqing", "5101": "chengdu", "4201": "wuhan", "3201": "nanjing",
    "1200": "tianjin", "2101": "shenyang", "2102": "dalian", "2201": "changchun",
    "2301": "haerbin", "3301": "hangzhou", "3302": "ningbo", "3501": "fuzhou",
    "3502": "xiamen", "3601": "nanchang", "3701": "jinan", "3702": "qingdao",
    "4101": "zhengzhou", "4301": "changsha", "4406": "foshan", "4419": "dongguan",
    "5301": "kunming", "6101": "xian", "6201": "lanzhou", "6501": "wulumuqi",
    "1301": "shijiazhuang", "3205": "suzhou", "3401": "hefei"
}

def fetch_city_data(city_code, city_name):
    url = f"https://map.amap.com/service/subway?srhdata={city_code}_drw_{city_name}.json"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except:
        return None

def main():
    # Collect all stations: {station_name: [(city, line), ...]}
    all_stations = defaultdict(list)

    print("Fetching metro data from all cities...")
    for code, name in CITIES.items():
        data = fetch_city_data(code, name)
        if not data:
            continue
        city_name = data.get('s', name)
        for line in data.get('l', []):
            line_name = line.get('ln', '')
            for station in line.get('st', []):
                station_name = station.get('n', '')
                if station_name:
                    all_stations[station_name].append((city_name, line_name))

    print(f"Total unique station names: {len(all_stations)}")

    # Find all reversed pairs
    station_names = list(all_stations.keys())
    reversed_pairs = []
    seen = set()

    for name in station_names:
        if len(name) < 2:
            continue
        reversed_name = name[::-1]
        if reversed_name in all_stations and reversed_name != name:
            pair_key = tuple(sorted([name, reversed_name]))
            if pair_key not in seen:
                seen.add(pair_key)
                reversed_pairs.append({
                    'station1': name,
                    'station1_locations': all_stations[name],
                    'station2': reversed_name,
                    'station2_locations': all_stations[reversed_name]
                })

    # Categorize results
    same_city_same_line = []
    same_city_cross_line = []
    cross_city = []

    for pair in reversed_pairs:
        cities1 = set(loc[0] for loc in pair['station1_locations'])
        cities2 = set(loc[0] for loc in pair['station2_locations'])

        common_cities = cities1 & cities2
        if common_cities:
            # Check if same line in any common city
            for city in common_cities:
                lines1 = set(loc[1] for loc in pair['station1_locations'] if loc[0] == city)
                lines2 = set(loc[1] for loc in pair['station2_locations'] if loc[0] == city)
                if lines1 & lines2:
                    same_city_same_line.append({
                        'city': city,
                        'lines': list(lines1 & lines2),
                        'station1': pair['station1'],
                        'station2': pair['station2']
                    })
                else:
                    same_city_cross_line.append({
                        'city': city,
                        'station1': pair['station1'],
                        'station1_lines': list(lines1),
                        'station2': pair['station2'],
                        'station2_lines': list(lines2)
                    })

        if not common_cities or cities1 != cities2:
            cross_city.append({
                'station1': pair['station1'],
                'station1_cities': list(cities1),
                'station2': pair['station2'],
                'station2_cities': list(cities2)
            })

    print("\n" + "="*60)
    print("NATIONWIDE METRO REVERSED STATION NAME ANALYSIS")
    print("="*60)

    print(f"\n【同线互逆】Same Line Reversals: {len(same_city_same_line)}")
    for item in same_city_same_line:
        print(f"  {item['city']} {item['lines']}: {item['station1']} ↔ {item['station2']}")

    print(f"\n【同城跨线】Same City Cross-Line: {len(same_city_cross_line)}")
    for item in same_city_cross_line:
        print(f"  {item['city']}: {item['station1']}({','.join(item['station1_lines'])}) ↔ {item['station2']}({','.join(item['station2_lines'])})")

    print(f"\n【跨城互逆】Cross-City Reversals: {len(cross_city)}")
    for item in cross_city:
        c1 = ','.join(item['station1_cities'])
        c2 = ','.join(item['station2_cities'])
        print(f"  {item['station1']}({c1}) ↔ {item['station2']}({c2})")

    # Save results
    results = {
        'same_line_reversals': same_city_same_line,
        'same_city_cross_line': same_city_cross_line,
        'cross_city_reversals': cross_city,
        'total_unique_stations': len(all_stations)
    }

    with open('nationwide_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to nationwide_analysis_results.json")

if __name__ == "__main__":
    main()
