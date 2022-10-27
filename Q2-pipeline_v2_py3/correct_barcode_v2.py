#!/usr/bin/python2
"""
correct_barcode_v2.py

Usage:
    correct_barcode_v2.py (-i input_file) (-b barcode_file) (-o output_file) (-m metric) (-d distance)
    correct_barcode_v2.py -h | --help
    correct_barcode_v2.py -v | --version

Options:
    -i input_file       Bam file resulted of TagReadWithGeneFunction
    -b barcode_file     Single-column file for designed barcode (No header)
    -o output_file      Bam file name for output of this program
    -m metric           The distance metric to be used. (seqlev or hamming)
    -d distance         Distance for error correction
    -h --help           Show this screen
    -v --version        Show version
"""

from __future__ import print_function

import time
import pandas as pd

from docopt import docopt

import pyper as pr
import pysam


def collect_set_XC(input_bam_file):

    bamfile = pysam.AlignmentFile(input_bam_file, "rb")

    set_XC = set()

    for read in bamfile:

        try:
            if read.get_tag('gn'):
                set_XC.add(read.get_tag('XC'))
        except:
            pass

    bamfile.close()

    return set_XC


def get_dict_correction(set_XC, designed_barcode,
                        metric="seqlev", distance="2"):

    if type(distance) not in (int, long):
        raise InvalidArgumentError

    if distance not in (0, 1, 2):
        print("distance must be 0, 1, or 2")
        raise InvalidArgumentError

    r = pr.R()
    r("library(DNABarcodes)")
    r.assign("list_XC", list(set_XC))
    r.assign("designed_barcode", designed_barcode)

    if metric == "seqlev":
        r("demultiplexed <- demultiplex(list_XC, designed_barcode, metric='seqlev')")
    elif metric == "hamming":
        r("demultiplexed <- demultiplex(list_XC, designed_barcode, metric='hamming')")
    else:
        print("metric must be 'seqlev' or 'hamming'")
        raise InvalidArgumentError

    df_correction = r.get("demultiplexed")

    df_correction.columns = [x.replace(" ", "") for x in df_correction.columns]
    df_correction_filt = (df_correction[df_correction.distance <= distance]
                          [['read', 'barcode']])
    dict_correct = df_correction_filt.set_index('read').to_dict()['barcode']

    return dict_correct


def correct_XC(input_file, dict_correct, output_file):

    input_bamfile = pysam.AlignmentFile(input_file, "rb")
    output_bamfile = pysam.AlignmentFile(output_file, "wb",
                                         template=input_bamfile)

    for read in input_bamfile:

        try:
            if read.get_tag('gn'):
                barcode = dict_correct[read.get_tag('XC')]
                read.set_tag('XC', barcode)
                output_bamfile.write(read)
        except:
            pass

    output_bamfile.close()
    input_bamfile.close()

#         try:
#             bef = read.get_tag('XC')
#             read.set_tag('XC', bef)
#         except:
#             pass

#         try:
#             barcode = dict_correct[read.get_tag('XC')]
#         except:
#             barcode = read.get_tag('XC')
#         read.set_tag('XC', barcode)


def InvalidArgumentError(ValueError):
    pass


if __name__ == '__main__':

    start = time.time()

    NAME = "correct_barcode_v2.py"
    VERSION = "0.1.0"

    args = docopt(__doc__, version="{0} {1}".format(NAME, VERSION))

    input_file = args['-i']
    barcode_file = args['-b']
    output_file = args['-o']
    metric = args['-m']
    distance = int(args['-d'])

    designed_barcode = list(pd.read_csv(barcode_file,
                                        header=None, squeeze=True))

    set_XC = collect_set_XC(input_file)

    dict_correct = get_dict_correction(set_XC, designed_barcode,
                                       metric=metric, distance=distance)

    correct_XC(input_file, dict_correct, output_file)

    elapsed_time = time.time() - start
    print("Program finished. Elapsed_time: {0:.2f}".format(elapsed_time) +
          " [sec]")

