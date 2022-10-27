#!/usr/bin/python2

from __future__ import print_function

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

metric = ('seqlev', )
distance = (2, )

base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "13_TagReadWithGeneFunction")
output_dir = os.path.join(base_dir, "results", "14_CorrectBarcode")

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

program_path = os.path.join(base_dir, "correct_barcode_v2.py")
barcode_file = os.path.join(base_dir, obj['BARCODE_FILE'])


input_files = glob.glob(os.path.join(input_dir, "*_gene_exon.bam"))

list_sh_file = []

threads_num = obj['THREADNUM']

for i, input_file in enumerate(input_files):

    sample_name = (os.path.split(input_file)[1].split(".")[0].
                   replace("_gene_exon", ""))

    for m in metric:

        for d in distance:

            output_file = os.path.join(output_dir,
                                       sample_name +
                                       "_" + m +
                                       "_d" + str(d) +
                                       ".bam")

            stdout_file = output_file.replace(".bam", ".o.txt")
            stderror_file = output_file.replace(".bam", ".e.txt")
            job_name = "Corr" + str(i) + "_" + m[0] + str(d)

            qsub_option = ("#!/bin/bash\n\n" +
                           "#$ -q " + obj['QUEUE_NODE'] + "\n" +
                           "#$ -notify\n" +
                           "#$ -N " + job_name + "\n" +
                           "#$ -o " + stdout_file + "\n" +
                           "#$ -e " + stderror_file + "\n" +
                           "#$ -pe threads " + str(threads_num) + "\n" +
                           "\n")

            docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

            docker_image = obj['PYPER_IMG']

            cmd = ("python2 " + program_path + " \\\n" +
                   "-i " + input_file + " \\\n" +
                   "-b " + barcode_file + " \\\n" +
                   "-o " + output_file + " \\\n" +
                   "-m " + m + " \\\n" +
                   "-d " + str(d) + " \\\n" +
                   "")

            sh_file = output_file.replace(".bam", ".sh")

            with open(sh_file, mode="w") as fh:
                fh.write(qsub_option)
                fh.write(docker_run_option + " \\\n")
                fh.write(docker_image + " \\\n")
                fh.write(cmd)
                os.chmod(sh_file, 0755)

            list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
