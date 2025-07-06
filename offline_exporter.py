# This program tries to parse distrowatch and create a svg graph simliar to: <https://en.wikipedia.org/wiki/Linux_distribution#/media/File:Linux_Distribution_Timeline_with_Android.svg>
# Copyright (C) 2016 Jappe Klooster
# Enhanced with offline export functionality

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
This module provides functionality to export scraped distribution data
in multiple formats for offline use and analysis.
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any
import strings


class OfflineExporter:
    """Handles exporting distro data in multiple formats for offline use."""

    def __init__(self, output_dir: str = "exports"):
        """Initialize the exporter with output directory."""
        self.output_dir = output_dir
        self.ensure_output_dir()

    def ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export_all_formats(self, distros_data: List[Dict[str, Any]], filename_prefix: str = "distros"):
        """Export data in all available formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{filename_prefix}_{timestamp}"

        results = {}

        # Export JSON (detailed format)
        results['json'] = self.export_json(distros_data, f"{base_filename}_detailed.json")

        # Export CSV (tabular format)
        results['csv'] = self.export_csv(distros_data, f"{base_filename}_table.csv")

        # Export simple text list
        results['txt'] = self.export_text_list(distros_data, f"{base_filename}_list.txt")

        # Export summary report
        results['summary'] = self.export_summary_report(distros_data, f"{base_filename}_summary.txt")

        # Export family tree structure
        results['tree'] = self.export_family_tree(distros_data, f"{base_filename}_tree.txt")

        return results

    def export_json(self, distros_data: List[Dict[str, Any]], filename: str) -> str:
        """Export data as JSON file."""
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(distros_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Exported detailed JSON to: {filepath}")
        return filepath

    def export_csv(self, distros_data: List[Dict[str, Any]], filename: str) -> str:
        """Export data as CSV file."""
        filepath = os.path.join(self.output_dir, filename)

        if not distros_data:
            return filepath

        # Get all unique keys from all distributions
        all_keys = set()
        for distro in distros_data:
            all_keys.update(distro.keys())

        # Sort keys for consistent ordering
        fieldnames = sorted(all_keys)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for distro in distros_data:
                # Convert lists to string representation for CSV
                row = {}
                for key in fieldnames:
                    value = distro.get(key, '')
                    if isinstance(value, list):
                        row[key] = ', '.join(str(v) for v in value)
                    else:
                        row[key] = str(value) if value is not None else ''
                writer.writerow(row)

        print(f"✓ Exported CSV table to: {filepath}")
        return filepath

    def export_text_list(self, distros_data: List[Dict[str, Any]], filename: str) -> str:
        """Export simple text list of distributions."""
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("Linux Distribution List\n")
            f.write("=" * 50 + "\n\n")

            for distro in distros_data:
                name = distro.get(strings.name, 'Unknown')
                human_name = distro.get('Human Name', name)
                status = distro.get(strings.status, 'Unknown')
                based_on = distro.get(strings.based, 'Unknown')

                f.write(f"• {human_name}\n")
                f.write(f"  Name: {name}\n")
                f.write(f"  Status: {status}\n")
                f.write(f"  Based on: {based_on}\n")

                # Add first release date if available
                dates = distro.get(strings.dates, [])
                if dates:
                    f.write(f"  First release: {dates[0]}\n")

                # Add link if available
                link = distro.get('Link', '')
                if link:
                    f.write(f"  Link: {link}\n")

                f.write("\n")

        print(f"✓ Exported text list to: {filepath}")
        return filepath

    def export_summary_report(self, distros_data: List[Dict[str, Any]], filename: str) -> str:
        """Export summary statistics report."""
        filepath = os.path.join(self.output_dir, filename)

        # Calculate statistics
        total_distros = len(distros_data)
        active_distros = sum(1 for d in distros_data if d.get(strings.status) == strings.active)
        inactive_distros = total_distros - active_distros

        # Count by base distribution
        base_counts = {}
        for distro in distros_data:
            base = distro.get(strings.based, 'Unknown')
            if base == strings.independend:
                base = 'Independent'
            elif ',' in base:
                base = base.split(',')[0]  # Take the first parent
            base_counts[base] = base_counts.get(base, 0) + 1

        # Count by decade
        decade_counts = {}
        for distro in distros_data:
            dates = distro.get(strings.dates, [])
            if dates:
                try:
                    year = int(dates[0].split('-')[0])
                    decade = f"{year//10*10}s"
                    decade_counts[decade] = decade_counts.get(decade, 0) + 1
                except (ValueError, IndexError):
                    pass

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("Distribution Summary Report\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Total Distributions: {total_distros}\n")
            f.write(f"Active Distributions: {active_distros}\n")
            f.write(f"Inactive Distributions: {inactive_distros}\n\n")

            f.write("Top Base Distributions:\n")
            f.write("-" * 30 + "\n")
            for base, count in sorted(base_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"{base}: {count}\n")

            f.write("\nDistributions by Decade:\n")
            f.write("-" * 30 + "\n")
            for decade, count in sorted(decade_counts.items()):
                f.write(f"{decade}: {count}\n")

            f.write(f"\nReport generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"✓ Exported summary report to: {filepath}")
        return filepath

    def export_family_tree(self, distros_data: List[Dict[str, Any]], filename: str) -> str:
        """Export family tree structure."""
        filepath = os.path.join(self.output_dir, filename)

        # Build family tree
        independents = []
        children_map = {}

        for distro in distros_data:
            name = distro.get(strings.name, 'Unknown')
            based_on = distro.get(strings.based, '')

            if based_on == strings.independend or not based_on:
                independents.append(distro)
            else:
                # For simplicity, take the first parent
                parent = based_on.split(',')[0] if ',' in based_on else based_on
                if parent not in children_map:
                    children_map[parent] = []
                children_map[parent].append(distro)

        def write_tree(f, distro, level=0):
            """Recursively write tree structure."""
            indent = "  " * level
            name = distro.get(strings.name, 'Unknown')
            human_name = distro.get('Human Name', name)
            status = distro.get(strings.status, '')

            status_marker = "●" if status == strings.active else "○"
            f.write(f"{indent}{status_marker} {human_name}\n")

            # Write children
            if name in children_map:
                for child in sorted(children_map[name], key=lambda x: x.get('Human Name', x.get(strings.name, ''))):
                    write_tree(f, child, level + 1)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("Distribution Family Tree\n")
            f.write("=" * 50 + "\n")
            f.write("● = Active, ○ = Inactive\n\n")

            # Write independent distributions first
            for distro in sorted(independents, key=lambda x: x.get('Human Name', x.get(strings.name, ''))):
                write_tree(f, distro)
                f.write("\n")

        print(f"✓ Exported family tree to: {filepath}")
        return filepath


def export_distros_offline(json_data: str, filename_prefix: str = "distros") -> Dict[str, str]:
    """
    Convenience function to export distro data in all formats.

    Args:
        json_data: JSON string containing distro data
        filename_prefix: Prefix for output files

    Returns:
        Dictionary with format -> filepath mappings
    """
    distros = json.loads(json_data)
    exporter = OfflineExporter()
    return exporter.export_all_formats(distros, filename_prefix)