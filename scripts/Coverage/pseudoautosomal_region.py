#!/usr/bin/env python3
__author__ = 'tomarovsky'
'''
Script for determining the coordinates of the pseudoautosomal region.
Output of coordinates to BED file.
'''
from Biocrutch.Statistics.coverage_statistics.CoverageMetrics import CoveragesMetrics
from Biocrutch.Statistics.pseudoautosomal_region.coordinator import Coordinator
from Biocrutch.Statistics.pseudoautosomal_region.filter import Filter
from Biocrutch.Routines.routine_functions import metaopen
from collections import Counter
from sys import stdin
import argparse


def coordinates_list_to_BED(chrom_name: str, coordinates: list) -> str:
    '''
    function to create BED format from a list of coordinates
    takes list [[start, stop], [start, stop]]
    '''
    result = ""
    for lst in coordinates:
        result += (chrom_name + '\t' + str(lst[0]) + '\t' + str(lst[1]) + '\n')
    return result


def main():
    print('---raw coordinates---')
    coordinates = Coordinator(args.input, float(args.whole_genome_value), args.deviation_percent)
    coordinates_and_medians_tuple = coordinates.get_coordinates(args.window_size,
                                                  args.coverage_column_name,
                                                  args.window_column_name, 
                                                  args.repeat_window_number)
    coords = coordinates_and_medians_tuple[0]
    medians = coordinates_and_medians_tuple[1]
    
    print(medians)
    print("Concatenate if the median >", round(coordinates.minimum_coverage, 2))
    print(coordinates_list_to_BED(args.scaffold_name, coords))

    print('--filtration by median--')
    coords_merge_by_median = Filter.concat_by_median(coords, # coordinates
                                              medians, # median list between regions
                                              coordinates.minimum_coverage,
                                              coordinates.maximum_coverage)
    print(coordinates_list_to_BED(args.scaffold_name, coords_merge_by_median))

    # print('--filtering by distance')
    # merge_by_distansce = Filter().concat_by_distanse(coords_merge_by_median, args.min_region_length)
    # print(coordinates_list_to_BED(args.scaffold_name, merge_by_distansce))

    if args.output:
        outF = open(args.output + "_pseudoreg.bed", "w")
        outF.writelines(coordinates_list_to_BED(args.scaffold_name, coords_merge_by_median))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script for determining the coordinates of the pseudoautosomal region. Output of coordinates to BED file.")

    group_required = parser.add_argument_group('Required options')
    group_required.add_argument('-i', '--input', type=lambda s: metaopen(s, "rt"),
                                help="input coverage_statistics_output.csv (don`t use for STDIN)", default=stdin)

    group_additional = parser.add_argument_group('Additional options')
    group_additional.add_argument('-o', '--output', metavar='PATH', type=str, default=False,
                                  help='output file prefix')
    group_additional.add_argument('-f', '--window-size', type=int,
                                  help="the window size used in your data", default=10000)
    group_additional.add_argument('--window_column_name', type=int,
                                  help="number of column in coverage file with window number", default=1)
    group_additional.add_argument('--coverage_column_name', type=int,
                                  help="number of column in coverage file with mean/median coverage per window", default=2)
    group_additional.add_argument('-s', '--scaffold-name', type=str,
                                  help="name of column in coverage file with scaffold name", default="scaffold")
    group_additional.add_argument('-m', '--whole_genome_value', type=str,
                                  help="whole genome median/mean value", default=34)
    group_additional.add_argument('-r', '--repeat_window_number', type=int,
                                  help="number of repeating windows for a given condition", default=10)
    group_additional.add_argument('-d', '--deviation_percent', type=int,
                                  help="measurement error", default=30)
    group_additional.add_argument('--min_region_length', type=int,
                                  help="minimal region length for filtration", default=10)

    args = parser.parse_args()
    main()
