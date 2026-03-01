# expr-metro-reversed-names

Analysis of reversed metro station names in China and globally.

## Question

> 全国的轨道交通中，有哪些像广州地铁6号线的河沙、沙河这样，一条线路上两个站名刚好互相颠倒的例子？

## Findings

### Same Line Character Reversal (1 pair)
| City | Line | Stations |
|------|------|----------|
| 广州 | 6号线 | 河沙 ↔ 沙河 |

**This is the only example in China!**

### Cross-Line Reversal (1 pair)
| City | Stations | Lines |
|------|----------|-------|
| 成都 | 光明 ↔ 明光 | 30号线 ↔ 19号线 |

### Homophones (2 pairs)
| City | Stations | Pinyin |
|------|----------|--------|
| 北京 | 关庄 = 管庄 | guānzhuāng |
| 广州 | 晓港 = 萧岗 | xiǎogǎng |

### Palindrome Stations (6)
- 园博园: Beijing, Shijiazhuang, Jinan, Wuhan, Chongqing
- 北海北: Beijing Line 6

## Data Source

- **Gaode Map Subway API**: `https://map.amap.com/service/subway?srhdata={city_code}_drw_{city}.json`
- **Coverage**: 31 cities, 291 lines, 6,462 stations

## Scripts

- `analyze_metro.py` - Basic same-line reversal analysis
- `analyze_metro_extended.py` - Extended analysis with palindromes
- `analyze_relaxed.py` - Relaxed constraints (cross-line, pinyin)

## Usage

```bash
pip install pypinyin
python analyze_relaxed.py
```

## Global Perspective

Checked international metro systems (Tokyo, Seoul, Taipei, Hong Kong):
- Japanese stations use kanji+kana, theoretically possible but rare
- Korean syllable blocks reversed usually don't form words
- Latin alphabet systems almost impossible

**Guangzhou Line 6's 河沙↔沙河 may be the only example globally.**

## Guangzhou Line 6 Fun Fact

Called "China's metro line with highest sand content":
横沙 → 沙贝 → 河沙 → 黄沙 → ... → 沙河顶 → 沙河

6 stations with 沙 (sand)! In Cantonese geography, 沙 represents small islands formed by river sediment.

## License

MIT

## Links

- [Zhihu Question](https://www.zhihu.com/question/2006005505311659847)
- [snolab](https://github.com/snolab)
