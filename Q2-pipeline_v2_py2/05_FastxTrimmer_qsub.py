#!/usr/bin/python2

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "03_fastq_ds")
output_dir = os.path.join(base_dir, "results", "05_fastx_trimmer")

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

input_files = glob.glob(os.path.join(input_dir, "*_R2_001.fastq.gz"))
list_sh_file = []

base_last = 62

threads_num = obj['THREADNUM']

for i, input_file in enumerate(input_files):
    sample_name = (os.path.split(input_file)[1].split(".")[0])

    if sample_name.startswith("Undetermined_"):
        continue

    output_file = os.path.join(output_dir, sample_name + ".fxtrim.fastq.gz")
    stdout_file = os.path.join(output_dir, sample_name + ".o.txt")
    stderror_file = os.path.join(output_dir, sample_name + ".e.txt")

    job_name = "FXT_" + str(i)

    qsub_option = ("#!/bin/bash\n\n" +
                   "#$ -q " + obj['QUEUE_NODE'] + "\n" +
                   "#$ -notify\n" +
                   "#$ -N " + job_name + "\n" +
                   "#$ -o " + stdout_file + "\n" +
                   "#$ -e " + stderror_file + "\n" +
                   "#$ -pe threads " + str(threads_num) + "\n\n")

    docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

    docker_image = obj['FASTXTOOLKIT_IMG']

    cmd = ("sh -c \"zcat " + input_file +
           " | fastx_trimmer -Q 33 -l " + str(base_last) +
           " | gzip - > " + output_file + "\"")

    sh_file = os.path.join(output_dir, sample_name + ".fxtrim.sh")

    with open(sh_file, mode="w") as fh:
        fh.write(qsub_option)
        fh.write(docker_run_option + " \\\n")
        fh.write(docker_image + " \\\n")
        fh.write(cmd)

    os.chmod(sh_file, 0755)

    list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)

