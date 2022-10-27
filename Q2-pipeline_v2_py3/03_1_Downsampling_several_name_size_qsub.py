#!/usr/bin/python3

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "01_fastq")
output_dir = os.path.join(base_dir, "results", "03_fastq_ds")

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

input_files = glob.glob(os.path.join(input_dir, "*_R1_001.fastq.gz"))
list_sh_file = []

seed = 1234
read_number_mega = [384, ]
job_count = 0

threads_num = obj['THREADNUM']

for i, input_file in enumerate(input_files):
    sample_name = (os.path.split(input_file)[1].split(".")[0].replace(
        "_R1_001", ""))

    if sample_name.startswith("Undetermined_"):
        continue

    for R in ["R1", "R2"]:
        for mega in read_number_mega:
            job_count += 1
            in_file = os.path.join(input_dir,
                                   sample_name + "_" + R + "_001.fastq.gz")
            out_file = os.path.join(output_dir, sample_name +
                                    "_ds" + str(mega).zfill(3) + "_" + R + "_001.fastq.gz")
            sh_file = os.path.join(output_dir, sample_name +
                                   "_ds" + str(mega).zfill(3) + "_" + R + ".sh")
            stdout_file = os.path.join(output_dir, sample_name +
                                       "_ds" + str(mega).zfill(3) + "_" + R + ".o.txt")
            stderror_file = os.path.join(output_dir, sample_name +
                                         "_ds" + str(mega).zfill(3) + "_" + R + ".e.txt")

            job_name = "ds" + str(job_count)

            qsub_option = ("#!/bin/bash\n\n" +
                           "#$ -q " + obj['QUEUE_NODE'] + "\n" +
                           "#$ -notify\n" +
                           "#$ -N " + job_name + "\n" +
                           "#$ -o " + stdout_file + "\n" +
                           "#$ -e " + stderror_file + "\n" +
                           "#$ -pe threads " + str(threads_num) + "\n\n")

            docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

            docker_image = obj['SEQTK_IMG']

            cmd = ("seqtk sample -s" + str(seed) + " " + in_file + " " + str(int(mega * 100000)) + " | gzip - > " + out_file + "\n")

            with open(sh_file, mode="w") as fh:
                fh.write(qsub_option)
                fh.write(docker_run_option + " \\\n")
                fh.write(docker_image + " \\\n")
                fh.write(cmd)

            os.chmod(sh_file, 0o755)

            list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
