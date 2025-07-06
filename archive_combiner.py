# This program tries to parse distrowatch and create a svg graph simliar to: <https://en.wikipedia.org/wiki/Linux_distribution#/media/File:Linux_Distribution_Timeline_with_Android.svg>
# Copyright (C) 2016 Jappe Klooster
# Enhanced with archive data combination functionality

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.If not, see <http://www.gnu.org/licenses/>.

"""
This module combines archive data from GLDT CSV with scraped DistroWatch data
to create a more comprehensive and accurate distribution dataset.
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Set
import strings


class ArchiveCombiner:
    """Combines GLDT archive data with scraped DistroWatch data."""

    def __init__(self, gldt_csv_path: str = "gldt.csv"):
        """Initialize with path to GLDT CSV file."""
        self.gldt_csv_path = gldt_csv_path
        self.archive_data = {}
        self.load_archive_data()

    def load_archive_data(self):
        """Load and parse the GLDT CSV archive data."""
        if not os.path.exists(self.gldt_csv_path):
            print(f"⚠️  Archive file {self.gldt_csv_path} not found")
            return

        print(f"📂 Loading archive data from {self.gldt_csv_path}...")

        with open(self.gldt_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)

            for row in reader:
                if not row or len(row) < 2:
                    continue

                # Skip comments and headers
                if row[0].startswith('//') or row[0].startswith('#') or row[0] == '':
                    continue

                # Process node entries (N = node)
                if row[0] == 'N' and len(row) >= 7:
                    self.parse_gldt_node(row)

        print(f"✓ Loaded {len(self.archive_data)} distributions from archive")

    def parse_gldt_node(self, row: List[str]):
        """Parse a single GLDT node entry."""
        try:
            name = row[1].strip().lower()
            color = row[2].strip() if len(row) > 2 else ""
            parent = row[3].strip().lower() if len(row) > 3 and row[3].strip() else None
            start_date = self.parse_gldt_date(row[4]) if len(row) > 4 and row[4].strip() else None
            end_date = self.parse_gldt_date(row[5]) if len(row) > 5 and row[5].strip() else None
            icon = row[6].strip() if len(row) > 6 else ""
            description = row[7].strip() if len(row) > 7 else ""

            # Handle name changes - GLDT format has name changes in columns 8+
            name_changes = []
            if len(row) > 8:
                i = 8
                while i < len(row) - 1:
                    if row[i].strip() and row[i+1].strip():
                        change_name = row[i].strip()
                        change_date = self.parse_gldt_date(row[i+1]) if row[i+1].strip() else None
                        if change_name and change_date:
                            name_changes.append({
                                "name": change_name,
                                "date": change_date,
                                "url": row[i+2].strip() if len(row) > i+2 else ""
                            })
                        i += 3
                    else:
                        break

            # Determine status
            status = strings.active if not end_date else "Inactive"

            # Build archive entry
            archive_entry = {
                strings.name: name,
                "Human Name": row[1].strip(),  # Keep original case for display
                "Color": color,
                strings.based: "independent" if not parent else parent,
                strings.dates: [start_date] if start_date else [],
                "End Date": end_date,
                strings.status: status,
                strings.image: icon,
                "Link": description if description.startswith('http') else "",
                "Description": description if not description.startswith('http') else "",
                "Name Changes": name_changes,
                "Source": "GLDT Archive"
            }

            # Add end date to dates if it exists and is different
            if end_date and end_date != start_date:
                archive_entry[strings.dates].append(end_date)

            self.archive_data[name] = archive_entry

        except Exception as e:
            print(f"⚠️  Error parsing GLDT row: {e}")

    def parse_gldt_date(self, date_str: str) -> str:
        """Convert GLDT date format (YYYY.MM.DD) to standard format (YYYY-MM-DD)."""
        if not date_str or date_str.strip() == "":
            return None

        try:
            # GLDT uses YYYY.MM.DD format
            date_str = date_str.strip()
            if '.' in date_str:
                parts = date_str.split('.')
                if len(parts) >= 1:
                    year = parts[0]
                    month = parts[1] if len(parts) > 1 else "01"
                    day = parts[2] if len(parts) > 2 else "01"
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            return None
        except Exception:
            return None

    def combine_with_scraped_data(self, scraped_json: str) -> str:
        """
        Combine archive data with scraped DistroWatch data.

        Args:
            scraped_json: JSON string of scraped data

        Returns:
            JSON string of combined data
        """
        print("🔄 Combining archive data with scraped data...")

        # Parse scraped data
        scraped_data = json.loads(scraped_json)
        scraped_names = {item.get(strings.name, '').lower() for item in scraped_data}

        # Start with scraped data as base
        combined_data = []
        enhanced_count = 0

        # Enhance scraped data with archive information
        for scraped_item in scraped_data:
            scraped_name = scraped_item.get(strings.name, '').lower()

            if scraped_name in self.archive_data:
                # Merge with archive data
                enhanced_item = self.merge_distribution_data(scraped_item, self.archive_data[scraped_name])
                combined_data.append(enhanced_item)
                enhanced_count += 1
            else:
                # Keep scraped data as is
                combined_data.append(scraped_item)

        # Add archive-only distributions (not found in scraped data)
        archive_only_count = 0
        for name, archive_item in self.archive_data.items():
            if name not in scraped_names:
                combined_data.append(archive_item)
                archive_only_count += 1

        print(f"✓ Enhanced {enhanced_count} scraped distributions with archive data")
        print(f"✓ Added {archive_only_count} distributions from archive only")
        print(f"✓ Total combined dataset: {len(combined_data)} distributions")

        return json.dumps(combined_data, indent=2)

    def merge_distribution_data(self, scraped: Dict[str, Any], archive: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge scraped distribution data with archive data.
        Priority: Archive data takes precedence for dates, relationships, and metadata.
        """
        merged = scraped.copy()

        # Archive data takes precedence for key fields
        if archive.get("Color"):
            merged["Color"] = archive["Color"]

        if archive.get("End Date"):
            merged["End Date"] = archive["End Date"]

        # Use archive dates if more complete
        archive_dates = archive.get(strings.dates, [])
        scraped_dates = scraped.get(strings.dates, [])

        if archive_dates:
            # Archive dates are usually more precise
            merged[strings.dates] = archive_dates
        elif scraped_dates:
            # Fallback to scraped dates
            merged[strings.dates] = scraped_dates

        # Use archive parent relationship if available
        archive_based = archive.get(strings.based)
        if archive_based and archive_based != "independent":
            merged[strings.based] = archive_based

        # Merge additional archive fields
        for field in ["Color", "Name Changes", "Description"]:
            if archive.get(field):
                merged[field] = archive[field]

        # Prefer archive URL if available and looks better
        archive_link = archive.get("Link", "")
        if archive_link and (not scraped.get("Link") or len(archive_link) > len(scraped.get("Link", ""))):
            merged["Link"] = archive_link

        # Mark as enhanced
        merged["Enhanced"] = "Combined with GLDT archive data"

        return merged

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the archive data."""
        if not self.archive_data:
            return {"error": "No archive data loaded"}

        total_distros = len(self.archive_data)
        active_distros = sum(1 for d in self.archive_data.values() if d.get(strings.status) == strings.active)
        inactive_distros = total_distros - active_distros

        # Count by decade
        decade_counts = {}
        for distro in self.archive_data.values():
            dates = distro.get(strings.dates, [])
            if dates:
                try:
                    year = int(dates[0].split('-')[0])
                    decade = f"{year//10*10}s"
                    decade_counts[decade] = decade_counts.get(decade, 0) + 1
                except (ValueError, IndexError):
                    pass

        return {
            "total_distributions": total_distros,
            "active_distributions": active_distros,
            "inactive_distributions": inactive_distros,
            "distributions_by_decade": decade_counts,
            "has_colors": sum(1 for d in self.archive_data.values() if d.get("Color")),
            "has_name_changes": sum(1 for d in self.archive_data.values() if d.get("Name Changes")),
        }


def combine_archive_with_scraped(scraped_json: str, gldt_csv_path: str = "gldt.csv") -> str:
    """
    Convenience function to combine archive data with scraped data.

    Args:
        scraped_json: JSON string of scraped DistroWatch data
        gldt_csv_path: Path to GLDT CSV file

    Returns:
        JSON string of combined data
    """
    combiner = ArchiveCombiner(gldt_csv_path)
    return combiner.combine_with_scraped_data(scraped_json)