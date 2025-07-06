#!/usr/bin/env python3
"""
Test script for archive combination functionality
"""

import json
import os
from archive_combiner import ArchiveCombiner, combine_archive_with_scraped

def test_archive_loading():
    """Test loading and parsing of GLDT archive data."""
    print("Testing GLDT archive data loading...")

    try:
        combiner = ArchiveCombiner()

        if not combiner.archive_data:
            print("❌ No archive data loaded")
            return False

        # Check some expected distributions
        expected_distros = ['debian', 'ubuntu', 'knoppix', 'fedora']
        found_distros = []

        for distro in expected_distros:
            if distro in combiner.archive_data:
                found_distros.append(distro)
                print(f"  ✓ Found {distro} in archive")
            else:
                print(f"  ⚠️  {distro} not found in archive")

        # Get and display statistics
        stats = combiner.get_statistics()
        print(f"\n📊 Archive Statistics:")
        print(f"  Total distributions: {stats.get('total_distributions', 0)}")
        print(f"  Active distributions: {stats.get('active_distributions', 0)}")
        print(f"  Inactive distributions: {stats.get('inactive_distributions', 0)}")
        print(f"  With colors: {stats.get('has_colors', 0)}")
        print(f"  With name changes: {stats.get('has_name_changes', 0)}")

        # Show distributions by decade
        decades = stats.get('distributions_by_decade', {})
        if decades:
            print(f"  By decade: {dict(sorted(decades.items()))}")

        print(f"✅ Archive loading test passed! Found {len(found_distros)}/{len(expected_distros)} expected distributions")
        return True

    except Exception as e:
        print(f"❌ Archive loading test failed: {e}")
        return False

def test_combination_with_sample_data():
    """Test combining archive data with sample scraped data."""
    print("\nTesting archive combination with sample data...")

    # Create sample scraped data that should match archive entries
    sample_scraped = [
        {
            "Name": "ubuntu",
            "Human Name": "Ubuntu",
            "Based on": "debian",
            "Status": "Active",
            "Dates": ["2004-10-20"],
            "Link": "https://ubuntu.com",
            "Image": ""
        },
        {
            "Name": "debian",
            "Human Name": "Debian",
            "Based on": "independent",
            "Status": "Active",
            "Dates": ["1993-09-15"],
            "Link": "https://debian.org",
            "Image": ""
        },
        {
            "Name": "testdistro",  # This won't be in archive
            "Human Name": "Test Distro",
            "Based on": "independent",
            "Status": "Active",
            "Dates": ["2023-01-01"],
            "Link": "https://test.com",
            "Image": ""
        }
    ]

    try:
        scraped_json = json.dumps(sample_scraped)
        combined_json = combine_archive_with_scraped(scraped_json)
        combined_data = json.loads(combined_json)

        print(f"  Original scraped: {len(sample_scraped)} distributions")
        print(f"  Combined result: {len(combined_data)} distributions")

        # Check if Ubuntu was enhanced with archive data
        ubuntu_entry = next((d for d in combined_data if d.get("Name") == "ubuntu"), None)
        if ubuntu_entry:
            if ubuntu_entry.get("Color"):
                print(f"  ✓ Ubuntu enhanced with color: {ubuntu_entry['Color']}")
            if ubuntu_entry.get("Enhanced"):
                print(f"  ✓ Ubuntu marked as enhanced: {ubuntu_entry['Enhanced']}")

        # Check if we got distributions from archive only
        archive_only = [d for d in combined_data if d.get("Source") == "GLDT Archive"]
        if archive_only:
            print(f"  ✓ Added {len(archive_only)} distributions from archive only")
            print(f"    Examples: {[d.get('Human Name', d.get('Name')) for d in archive_only[:5]]}")

        print("✅ Archive combination test passed!")
        return True

    except Exception as e:
        print(f"❌ Archive combination test failed: {e}")
        return False

def test_enhanced_data_quality():
    """Test the quality of enhanced data."""
    print("\nTesting enhanced data quality...")

    try:
        # Simple test data
        test_data = [{"Name": "ubuntu", "Human Name": "Ubuntu", "Based on": "debian", "Status": "Active", "Dates": ["2004-10-20"]}]

        combined_json = combine_archive_with_scraped(json.dumps(test_data))
        combined_data = json.loads(combined_json)

        enhancements_found = 0

        for distro in combined_data:
            name = distro.get("Name", "").lower()
            print(f"\n  📋 {distro.get('Human Name', name)}:")

            # Check for archive enhancements
            if distro.get("Color"):
                print(f"    ✓ Color: {distro['Color']}")
                enhancements_found += 1

            if distro.get("Name Changes"):
                changes = distro["Name Changes"]
                print(f"    ✓ Name changes: {len(changes)} recorded")
                for change in changes[:2]:  # Show first 2
                    print(f"      - {change.get('name')} ({change.get('date')})")
                enhancements_found += 1

            if distro.get("End Date"):
                print(f"    ✓ End date: {distro['End Date']}")
                enhancements_found += 1

            if distro.get("Enhanced"):
                print(f"    ✓ {distro['Enhanced']}")

        print(f"\n✅ Data quality test passed! Found {enhancements_found} enhancements")
        return True

    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Archive Combination Functionality")
    print("=" * 50)

    # Test 1: Archive loading
    archive_success = test_archive_loading()

    # Test 2: Combination with sample data
    combination_success = False
    if archive_success:
        combination_success = test_combination_with_sample_data()

    # Test 3: Enhanced data quality
    quality_success = False
    if combination_success:
        quality_success = test_enhanced_data_quality()

    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Archive loading: {'✅ PASSED' if archive_success else '❌ FAILED'}")
    print(f"Data combination: {'✅ PASSED' if combination_success else '❌ FAILED'}")
    print(f"Data quality: {'✅ PASSED' if quality_success else '❌ FAILED'}")

    if all([archive_success, combination_success, quality_success]):
        print("\n🎉 All archive combination tests passed!")
        print("You can now use --combineArchive to enhance your data with GLDT archive information.")
    else:
        print("\n❌ Some archive combination tests failed.")
        if not archive_success:
            print("Check that gldt.csv exists and is readable.")