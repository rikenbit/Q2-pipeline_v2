#!/usr/bin/python2

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "08_TrimDropseq")
output_dir = os.path.join(base_dir, "results", "09_SamToFastq")

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

input_files = glob.glob(os.path.join(input_dir, "*_trim_adapter_polyA.bam"))
list_sh_file = []

threads_num = obj['THREADNUM']

for i, input_file in enumerate(input_files):
    sample_name = (os.path.split(input_file)[1].split(".")[0])
    output_file = os.path.join(output_dir, sample_name + ".fastq")
    stdout_file = os.path.join(output_dir, sample_name + ".o.txt")
    stderror_file = os.path.join(output_dir, sample_name + ".e.txt")

    job_name = "Sam2Fa_" + str(i)

    qsub_option = ("#!/bin/bash\n\n" +
                   "#$ -q " + obj['QUEUE_NODE'] + "\n" +
                   "#$ -notify\n" +
                   "#$ -N " + job_name + "\n" +
                   "#$ -o " + stdout_file + "\n" +
                   "#$ -e " + stderror_file + "\n" +
                   "#$ -pe threads " + str(threads_num) + "\n\n")

    docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

    docker_image = obj['PICARD_IMG']

    cmd = ("java -XX:ParallelGCThreads=" + str(threads_num) + " -Xmx128g \\\n" +
           "-Djava.io.tmpdir=" + output_dir + " \\\n" +
           "-jar /usr/local/bin/picard.jar SamToFastq \\\n" +
           "INPUT=" + input_file + " \\\n" +
           "FASTQ=" + output_file + " \\\n" +
           "TMP_DIR=" + output_dir + " \\\n" +
           "")

    sh_file = os.path.join(output_dir, sample_name + ".SamToFastq.sh")

    with open(sh_file, mode="w") as fh:
        fh.write(qsub_option)
        fh.write(docker_run_option + " \\\n")
        fh.write(docker_image + " \\\n")
        fh.write(cmd)

    os.chmod(sh_file, 0755)

    list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
