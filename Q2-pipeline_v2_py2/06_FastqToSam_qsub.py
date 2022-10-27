#!/usr/bin/python2

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

base_dir = os.getcwd()
input_dir_R1 = os.path.join(base_dir, "results", "03_fastq_ds")
input_dir_R2 = os.path.join(base_dir, "results", "05_fastx_trimmer")
output_dir = os.path.join(base_dir, "results", "06_FastqToSam")

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

input_files = glob.glob(os.path.join(input_dir_R1, "*_R1_001.fastq.gz"))
list_sh_file = []

quality_format = "Standard"
sample_name_header = "development"
sort_order = "queryname"

threads_num = obj['THREADNUM']

for i, input_file in enumerate(input_files):
    sample_name = (os.path.split(input_file)[1].split(".")[0].
                   replace("_R1_001", ""))

    if sample_name.startswith("Undetermined_"):
        continue

    input_file_R1 = input_file
    input_file_R2 = os.path.join(input_dir_R2,
                                 sample_name + "_R2_001.fxtrim.fastq.gz")
    output_file = os.path.join(output_dir, sample_name + ".bam")

    stdout_file = os.path.join(output_dir, sample_name + ".o.txt")
    stderror_file = os.path.join(output_dir, sample_name + ".e.txt")

    job_name = "F2S_" + str(i)

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
           "    -Djava.io.tmpdir=" + output_dir + " \\\n" +
           "    -jar /usr/local/bin/picard.jar FastqToSam \\\n" +
           "    FASTQ=" + input_file_R1 + " \\\n" +
           "    FASTQ2=" + input_file_R2 + " \\\n" +
           "    QUALITY_FORMAT=" + quality_format + " \\\n" +
           "    OUTPUT=" + output_file + " \\\n" +
           "    SAMPLE_NAME=" + sample_name_header + " \\\n" +
           "    SORT_ORDER=" + sort_order + " \\\n" +
           "    TMP_DIR=" + output_dir + "")

    sh_file = os.path.join(output_dir, sample_name + ".FastqToSam.sh")

    with open(sh_file, mode="w") as fh:
        fh.write(qsub_option)
        fh.write(docker_run_option + " \\\n")
        fh.write(docker_image + " \\\n")
        fh.write(cmd)

    os.chmod(sh_file, 0755)

    list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
