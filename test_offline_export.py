#!/usr/bin/env python3
"""
Test script for offline export functionality
"""

import json
import os
import sys
from fetchdists import fetch_dist_list_from
from offline_exporter import export_distros_offline

def test_with_sample_data():
    """Test with hardcoded sample data for quick validation."""
    sample_data = [
        {
            "Name": "ubuntu",
            "Human Name": "Ubuntu",
            "Based on": "debian",
            "Status": "Active",
            "Dates": ["2004-10-20"],
            "Link": "https://ubuntu.com",
            "Image": "ubuntu.png"
        },
        {
            "Name": "debian",
            "Human Name": "Debian",
            "Based on": "independent",
            "Status": "Active",
            "Dates": ["1993-09-15"],
            "Link": "https://debian.org",
            "Image": "debian.png"
        },
        {
            "Name": "mint",
            "Human Name": "Linux Mint",
            "Based on": "ubuntu",
            "Status": "Active",
            "Dates": ["2006-08-27"],
            "Link": "https://linuxmint.com",
            "Image": "mint.png"
        }
    ]

    print("Testing offline export with sample data...")
    json_data = json.dumps(sample_data)

    try:
        results = export_distros_offline(json_data, "test_sample")
        print("\n✅ Sample data export successful!")
        print("Files created:")
        for format_type, filepath in results.items():
            print(f"  {format_type}: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Sample data export failed: {e}")
        return False

def test_limited_real_data():
    """Test with limited real data from DistroWatch."""
    print("\nTesting with limited real data from DistroWatch...")
    print("This will scrape only a few distributions for testing...")

    try:
        # Use a very restrictive search to limit results
        limited_search = "ostype=Linux&category=Desktop&origin=All&basedon=All&notbasedon=None&desktop=All&architecture=All&package=All&rolling=All&isosize=All&netinstall=All&status=Active"

        print("Fetching limited data from DistroWatch...")
        json_data = fetch_dist_list_from("https://distrowatch.com", limited_search)

        # Parse to check how many we got
        data = json.loads(json_data)
        print(f"Retrieved {len(data)} distributions")

        # If we got too many, take just the first 10 for testing
        if len(data) > 10:
            print("Limiting to first 10 distributions for testing...")
            data = data[:10]
            json_data = json.dumps(data)

        results = export_distros_offline(json_data, "test_real_limited")
        print("\n✅ Limited real data export successful!")
        print("Files created:")
        for format_type, filepath in results.items():
            print(f"  {format_type}: {filepath}")
        return True

    except Exception as e:
        print(f"❌ Limited real data export failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Offline Export Functionality")
    print("=" * 40)

    # Test 1: Sample data
    sample_success = test_with_sample_data()

    # Test 2: Limited real data (only if sample worked)
    real_success = False
    if sample_success:
        user_input = input("\n⚠️  Fetch limited real data from DistroWatch? (y/n): ").lower()
        if user_input == 'y':
            real_success = test_limited_real_data()

    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Sample data: {'✅ PASSED' if sample_success else '❌ FAILED'}")
    print(f"Real data: {'✅ PASSED' if real_success else '⏭️ SKIPPED'}")

    if sample_success:
        print("\n🎉 Offline export functionality is working!")
        print("You can now use the export_distros_offline() function to save distro data offline.")
    else:
        print("\n❌ There are issues with the offline export functionality.")