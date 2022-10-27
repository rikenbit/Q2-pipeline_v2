#!/usr/bin/python3

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "06_FastqToSam")
output_dir = os.path.join(base_dir, "results",
                          "07_TagBamWithReadSequenceExtended")

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

input_files = glob.glob(os.path.join(input_dir, "*.bam"))
list_sh_file = []

threads_num = obj['THREADNUM']

if obj['CB_LENGTH'] == '14':
    CBLEN_1 = ("1-14")
    CBLEN_2 = ("15-22")
elif obj['CB_LENGTH'] == '15':
    CBLEN_1 = ("1-15")
    CBLEN_2 = ("15-23")

for i, input_file in enumerate(input_files):
    sample_name = (os.path.split(input_file)[1].split(".")[0])
    output_file_cell = os.path.join(output_dir, sample_name + "_Cell.bam")
    summary_file_cell = os.path.join(output_dir, sample_name +
                                     "_Cell.bam_summary.txt")
    output_file_cell_mol = os.path.join(output_dir, sample_name +
                                        "_CellMol.bam")
    summary_file_cell_mol = os.path.join(output_dir, sample_name +
                                         "_CellMol.bam_summary.txt")
    output_file_filtered = os.path.join(output_dir, sample_name +
                                        "_filtered.bam")

    stdout_file = os.path.join(output_dir, sample_name + ".o.txt")
    stderror_file = os.path.join(output_dir, sample_name + ".e.txt")

    job_name = "TBR_" + str(i)

    qsub_option = ("#!/bin/bash\n\n" +
                   "#$ -q " + obj['QUEUE_NODE'] + "\n" +
                   "#$ -notify\n" +
                   "#$ -N " + job_name + "\n" +
                   "#$ -o " + stdout_file + "\n" +
                   "#$ -e " + stderror_file + "\n" +
                   "#$ -pe threads " + str(threads_num) + "\n\n")

    docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

    docker_image = obj['DROPSEQ_IMG']

    cmd_1 = ("TagBamWithReadSequenceExtended \\\n" +
             "    INPUT=" + input_file + " \\\n" +
             "    OUTPUT=" + output_file_cell + " \\\n" +
             "    SUMMARY=" + summary_file_cell + " \\\n" +
             "    BASE_RANGE=" + CBLEN_1 + " \\\n" +
             "    BASE_QUALITY=10 \\\n" +
             "    BARCODED_READ=1 \\\n" +
             "    DISCARD_READ=FALSE \\\n" +
             "    TAG_NAME=XC \\\n" +
             "    NUM_BASES_BELOW_QUALITY=1")

    cmd_2 = ("TagBamWithReadSequenceExtended \\\n" +
             "    INPUT=" + output_file_cell + " \\\n" +
             "    OUTPUT=" + output_file_cell_mol + " \\\n" +
             "    SUMMARY=" + summary_file_cell_mol + " \\\n" +
             "    BASE_RANGE=" + CBLEN_2 + " \\\n" +
             "    BASE_QUALITY=10 \\\n" +
             "    BARCODED_READ=1 \\\n" +
             "    DISCARD_READ=True \\\n" +
             "    TAG_NAME=XM \\\n" +
             "    NUM_BASES_BELOW_QUALITY=1")

    cmd_3 = ("FilterBam \\\n" +
             "    TAG_REJECT=XQ \\\n" +
             "    INPUT=" + output_file_cell_mol + " \\\n" +
             "    OUTPUT=" + output_file_filtered + "")

    sh_file = os.path.join(output_dir, sample_name + ".TagBam.sh")

    with open(sh_file, mode="w") as fh:
        fh.write(qsub_option)
        fh.write(docker_run_option + " \\\n")
        fh.write(docker_image + " \\\n")
        fh.write(cmd_1 + "\n\n")
        fh.write(docker_run_option + " \\\n")
        fh.write(docker_image + " \\\n")
        fh.write(cmd_2 + "\n\n")
        fh.write(docker_run_option + " \\\n")
        fh.write(docker_image + " \\\n")
        fh.write(cmd_3)

    os.chmod(sh_file, 0o755)

    list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
