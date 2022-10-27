#!/usr/bin/python3

import os
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

base_dir = os.getcwd()

run_dir = obj['BCL_DIR']

input_dir = os.path.join(run_dir,
                         "Data",
                         "Intensities",
                         "BaseCalls")

output_dir = os.path.join(base_dir, "results", "01_fastq")

interop_dir = os.path.join(output_dir, "interop")
reports_dir = os.path.join(output_dir, "reports")
stats_dir = os.path.join(output_dir, "stats")

for d in [output_dir, interop_dir, reports_dir, stats_dir]:
    if not os.path.isdir(d):
        os.makedirs(d)

sample_sheet_file = os.path.join(run_dir, obj['SAMPLESHEET'])

stdout_file = os.path.join(output_dir, "bcl2fastq2.o.txt")

stderror_file = os.path.join(output_dir, "bcl2fastq2.e.txt")

threads_num = obj['THREADNUM']

job_name = "B2Q"

qsub_option = ("#!/bin/bash\n\n" +
               "#$ -q " + obj['QUEUE_NODE'] + "\n" +
               "#$ -notify\n" +
               "#$ -N " + job_name + "\n" +
               "#$ -o " + stdout_file + "\n" +
               "#$ -e " + stderror_file + "\n" +
               "#$ -pe threads " + str(threads_num) + "\n\n")

docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

docker_image = obj['BCL2FASTQ_IMG']

cmd = ("bcl2fastq --no-lane-splitting \\\n" +
       "    --runfolder-dir " + run_dir + " \\\n" +
       "    --input-dir " + input_dir + " \\\n" +
       "    --output-dir " + output_dir + " \\\n" +
       "    --interop-dir " + interop_dir + " \\\n" +
       "    --reports-dir " + reports_dir + " \\\n" +
       "    --stats-dir " + stats_dir + " \\\n" +
       "    --sample-sheet " + sample_sheet_file + " \\\n" +
       "    --minimum-trimmed-read-length 20 \\\n" +
       "    --mask-short-adapter-reads 20 \\\n" +
       "    --create-fastq-for-index-reads \\\n" +
       "    --barcode-mismatches 1 \\\n" +
       "    ")

sh_file = os.path.join(output_dir, "bcl2fastq2.sh")

with open(sh_file, mode="w") as fh:
    fh.write(qsub_option)
    fh.write(docker_run_option + " \\\n")
    fh.write(docker_image + " \\\n")
    fh.write(cmd)

os.chmod(sh_file, 0o755)

subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)

