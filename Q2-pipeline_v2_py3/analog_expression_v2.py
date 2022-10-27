#!/usr/bin/python2
"""
analog_expression_v2.py

Usage:
    analog_expression.py (-i input_file) (-b barcode_file) (-g gtf_file) (-o output_file)
    analog_expression.py -h | --help
    analog_expression.py -v | --version

Options:
    -i input_file       Bam file resulted of correct_barcode_v2.py
    -b barcode_file     Single-column file for barcode sequences (No header)
    -g gtf_file         GTF file name for getting list of gene names
    -o output_file      Bam file name for output of this program
    -h --help           Show this screen
    -v --version        Show version
"""

from __future__ import print_function

import re
import time
import pandas as pd

from docopt import docopt

import pysam


def get_genename(str):

    regexp = re.compile('gene_name "(\S+)"')
    m = regexp.search(str)

    if m is not None:
        return m.group(1)


def make_genelist(gtf_file):

    df = pd.read_csv(gtf_file, sep="\t", skiprows=0, header=None)
    list_gene = list({get_genename(x) for x in df[8]})
    return list_gene


def count_GE_read(input_bam_file, list_barcode, list_gene):

    df_exp = pd.DataFrame(index=list_gene, columns=list_barcode,
                          ).fillna(0)

    bamfile = pysam.AlignmentFile(input_bam_file, "rb")

    for read in bamfile:
        try:
            XC_tag = read.get_tag('XC')
            GE_tag = read.get_tag('gn')
            if read.get_tag('NH') == 1:
                df_exp[XC_tag][GE_tag] += 1
        except:
            pass

    bamfile.close()

    return df_exp


if __name__ == '__main__':

    start = time.time()

    NAME = "analog_expression_v2.py"
    VERSION = "0.1.0"

    args = docopt(__doc__, version="{0} {1}".format(NAME, VERSION))

    input_file = args['-i']
    barcode_file = args['-b']
    gtf_file = args['-g']
    output_file = args['-o']

    list_barcode = list(pd.read_csv(barcode_file, header=None, squeeze=True))

    list_gene = make_genelist(gtf_file)

    df = count_GE_read(input_file, list_barcode, list_gene)

    df.to_csv(output_file, sep="\t", index_label="GENE")

    elapsed_time = time.time() - start

    print("Program finished. Elapsed_time: {0:.2f}".format(elapsed_time) +
          " [sec]")
