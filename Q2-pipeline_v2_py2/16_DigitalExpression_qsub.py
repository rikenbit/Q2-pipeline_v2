#!/usr/bin/python2

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

# directoris
base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "14_CorrectBarcode")
cell_bc_file = os.path.join(base_dir, obj['BARCODE_FILE'])
output_dir = os.path.join(base_dir, "results", "16_DigitalExpression")

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

# make sh files
input_files = glob.glob(os.path.join(input_dir, "*.bam"))
list_sh_file = []

threads_num = obj['THREADNUM']

for i, input_file in enumerate(input_files):
    sample_name = os.path.split(input_file)[1].split(".")[0]

    output_file = os.path.join(output_dir,
                               sample_name + "_dge.txt.gz")
    summary_file = os.path.join(output_dir,
                                sample_name + "_dge.summary.txt")
    stdout_file = os.path.join(output_dir, sample_name + ".o.txt")
    stderror_file = os.path.join(output_dir, sample_name + ".e.txt")
    job_name = "DigExp" + str(i)

    qsub_option = ("#!/bin/bash\n\n" +
                   "#$ -q " + obj['QUEUE_NODE'] + "\n" +
                   "#$ -notify\n" +
                   "#$ -N " + job_name + "\n" +
                   "#$ -o " + stdout_file + "\n" +
                   "#$ -e " + stderror_file + "\n" +
                   "#$ -pe threads " + str(threads_num) + "\n" +
                   "\n")

    docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

    docker_image = obj['DROPSEQ_IMG']

    cmd = ("DigitalExpression \\\n" +
           "    I=" + input_file + " \\\n" +
           "    O=" + output_file + " \\\n" +
           "    SUMMARY=" + summary_file + " \\\n" +
           "    CELL_BC_FILE=" + cell_bc_file + " \\\n" +
           "    ")

    sh_file = os.path.join(output_dir, sample_name + ".DigitalExpression.sh")

    with open(sh_file, mode="w") as fh:
        fh.write(qsub_option)
        fh.write(docker_run_option + " \\\n")
        fh.write(docker_image + " \\\n")
        fh.write(cmd)
        os.chmod(sh_file, 0755)

    list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
