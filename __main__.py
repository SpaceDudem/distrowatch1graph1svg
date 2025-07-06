# This program tries to parse distrowatch and create a svg graph simliar to: <https://en.wikipedia.org/wiki/Linux_distribution#/media/File:Linux_Distribution_Timeline_with_Android.svg>
# Copyright (C) 2016 Jappe Klooster

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
This file glues the program together, it'll also try to execute gnuclad
and inkscape for the png once finished. Once fetching the distro's has been
completed they'll be cached in out, delete that file to re-download
"""

from fetchdists import fetch_dist_list_from
from graph import to_graph
from svg import toCSV
from offline_exporter import export_distros_offline
from archive_combiner import combine_archive_with_scraped
from subprocess import call

import os
import argparse
import json


def main():
    parser = argparse.ArgumentParser(
        description=""" Distrograph Copyright (C) 2016 Jappie Klooster
                        This program comes with ABSOLUTELY NO WARRANTY;
                        for details see the LICENSE file.
                        This is free software,
                        and you are welcome to redistribute it under certain
                        conditions; see the LICENSE file for details"""
        )
    parser.add_argument(
        '--baseurl',
        default="https://distrowatch.com",
        help="default http://distrowatch.com"
    )
    parser.add_argument(
        '--searchOptions',
        default="ostype=All&category=All&origin=All&basedon=All" +
        "&notbasedon=None" +
        "&desktop=All&architecture=All&package=All&rolling=All&isosize=All" +
        "&netinstall=All&status=All",
        help="""the GET form generates this at distrowatch.com/search.php
                everything behind the ? can be put in here,
                use this to add constraints to your graph,
                for example if you're only interested in active distro's,
                specify it at the form and copy the resulting GET request in
                this argument"""
    )
    parser.add_argument(
        '--exportOffline',
        action='store_true',
        help="""Export scraped distribution data in multiple formats for offline use
                (JSON, CSV, TXT, Summary, Family Tree)"""
    )
    parser.add_argument(
        '--exportOnly',
        action='store_true',
        help="""Only export offline data, skip SVG generation
                (useful for data analysis without creating graphs)"""
    )
    parser.add_argument(
        '--combineArchive',
        action='store_true',
        help="""Combine scraped data with GLDT archive data for more complete dataset
                (includes historical distributions, colors, precise dates)"""
    )

    args = parser.parse_args()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    outputdir = "out"
    if not os.path.isdir(outputdir):
        os.mkdir(outputdir)
    os.chdir(outputdir)

    fetched_dists_file = "dists.json"
    son = ""
    if os.path.isfile(fetched_dists_file):
        with open(fetched_dists_file, "r") as cached:
            print("using cached file %s/%s" % (outputdir, fetched_dists_file))
            son = "".join(cached.readlines())
    if son == "":
        url = args.baseurl
        print("fetching distros from %s" % url)
        son = fetch_dist_list_from(url, args.searchOptions)
        with open(fetched_dists_file, "w") as cached:
            print("wrote cache file %s/%s" % (outputdir, fetched_dists_file))
            cached.write(son)

    # Combine with archive data if requested
    if args.combineArchive:
        print("🔄 Combining with GLDT archive data...")
        try:
            original_count = len(json.loads(son))
            # Pass correct path to gldt.csv (go up one directory from 'out')
            gldt_path = "../gldt.csv"
            son = combine_archive_with_scraped(son, gldt_path)
            combined_count = len(json.loads(son))
            print(f"✅ Archive combination completed!")
            print(f"   Original: {original_count} distributions")
            print(f"   Combined: {combined_count} distributions")
            print(f"   Added: {combined_count - original_count} from archive")

            # Save combined data to cache
            combined_file = "dists_combined.json"
            with open(combined_file, "w") as cached:
                print("wrote combined cache file %s/%s" % (outputdir, combined_file))
                cached.write(son)
        except Exception as e:
            print(f"❌ Archive combination failed: {e}")
            print("Continuing with scraped data only...")

    # Export offline data if requested
    if args.exportOffline or args.exportOnly:
        print("Exporting offline data...")
        try:
            export_results = export_distros_offline(son, "distrowatch_data")
            print("✅ Offline export completed successfully!")
            print("Export files created:")
            for format_type, filepath in export_results.items():
                print(f"  {format_type}: {filepath}")
        except Exception as e:
            print(f"❌ Offline export failed: {e}")

    # Skip SVG generation if exportOnly is specified
    if args.exportOnly:
        print("Skipping SVG generation (--exportOnly specified)")
        return

    son = to_graph(son)

    csv = toCSV(json.loads(son), "").result
    csvfile = "dists.csv"
    print("writing csv to %s/%s" % (outputdir, csvfile))
    with open(csvfile, "w") as cached:
        cached.write(csv)
    os.chdir("../")
    call("gnuclad %s/%s dists.svg gnuclad.conf" % (outputdir, csvfile),
         shell=True)
    call("inkscape -z -e dists.png dists.svg", shell=True)

if __name__ == "__main__":
    main()
