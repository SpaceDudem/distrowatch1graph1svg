# Offline Export Usage Guide

## Overview
The enhanced distrowatch scraper now supports exporting distribution data in multiple formats for offline use and analysis. This is perfect for creating personal lists, data analysis, or research purposes.

## Command Line Usage

### Basic Export (with SVG generation)
```bash
python __main__.py --exportOffline
```

### Export Only (skip SVG generation)
```bash
python __main__.py --exportOnly
```

### Export with Custom Search Options
```bash
python __main__.py --exportOnly --searchOptions "ostype=Linux&category=Desktop&status=Active"
```

## Output Formats

When you run the export, you'll get 5 different files:

1. **Detailed JSON** (`*_detailed.json`)
   - Complete structured data with all fields
   - Perfect for programmatic processing

2. **CSV Table** (`*_table.csv`)
   - Tabular format for spreadsheet applications
   - Easy to import into Excel, LibreOffice, etc.

3. **Text List** (`*_list.txt`)
   - Human-readable list format
   - Shows name, status, based on, release date, and link

4. **Summary Report** (`*_summary.txt`)
   - Statistical analysis of the data
   - Counts by base distribution, decade, status

5. **Family Tree** (`*_tree.txt`)
   - Visual hierarchy of distributions
   - Shows parent-child relationships
   - ● = Active, ○ = Inactive

## Example Output

### Text List Sample
```
Linux Distribution List
==================================================

• Ubuntu
  Name: ubuntu
  Status: Active
  Based on: debian
  First release: 2004-10-20
  Link: https://ubuntu.com

• Debian
  Name: debian
  Status: Active
  Based on: independent
  First release: 1993-09-15
  Link: https://debian.org
```

### Family Tree Sample
```
Distribution Family Tree
==================================================
● = Active, ○ = Inactive

● Debian
  ● Ubuntu
    ● Linux Mint
```

## Search Options

Use DistroWatch's search form to generate custom search options:

1. Go to https://distrowatch.com/search.php
2. Set your filters (OS type, category, status, etc.)
3. Click "Search"
4. Copy the URL parameters after the "?" in the URL
5. Use with `--searchOptions` parameter

Example filters:
- `ostype=Linux` - Only Linux distributions
- `status=Active` - Only active distributions
- `category=Desktop` - Only desktop distributions
- `basedon=Debian` - Only Debian-based distributions

## Tips

- The export files are timestamped, so you can track changes over time
- Use `--exportOnly` to avoid the SVG generation dependencies
- Start with restrictive search options to avoid overwhelming DistroWatch
- The JSON format is perfect for further processing with other tools
- CSV format works great for data analysis in spreadsheet applications

## Programmatic Usage

```python
from fetchdists import fetch_dist_list_from
from offline_exporter import export_distros_offline

# Fetch data
json_data = fetch_dist_list_from("https://distrowatch.com", "ostype=Linux&status=Active")

# Export in all formats
results = export_distros_offline(json_data, "my_distros")

# Results is a dict with format -> filepath mappings
print(f"JSON exported to: {results['json']}")
print(f"CSV exported to: {results['csv']}")
```

## Files Location

All export files are saved in the `exports/` directory with timestamps to avoid conflicts.