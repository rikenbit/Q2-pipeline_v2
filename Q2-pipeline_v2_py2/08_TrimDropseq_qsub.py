#!/usr/bin/python2

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "07_TagBamWithReadSequenceExtended")
output_dir = os.path.join(base_dir, "results", "08_TrimDropseq")

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

input_files = glob.glob(os.path.join(input_dir, "*_filtered.bam"))
list_sh_file = []

threads_num = obj['THREADNUM']

for i, input_file in enumerate(input_files):

    sample_name = (os.path.split(input_file)[1].split(
        ".")[0]).replace("_filtered", "")
    output_file_adapter = os.path.join(output_dir, sample_name +
                                       "_trim_adapter.bam")
    summary_file_adapter = os.path.join(output_dir, sample_name +
                                        "_trim_adapter.bam_summary.txt")
    output_file_adapter_polyA = os.path.join(output_dir, sample_name +
                                             "_trim_adapter_polyA.bam")
    summary_file_adapter_polyA = os.path.join(output_dir, sample_name +
                                              "_trim_adapter_polyA.bam_summary.txt")

    stdout_file = os.path.join(output_dir, sample_name + ".o.txt")
    stderror_file = os.path.join(output_dir, sample_name + ".e.txt")

    job_name = "TrDr" + str(i)

    qsub_option = ("#!/bin/bash\n\n" +
                   "#$ -q " + obj['QUEUE_NODE'] + "\n" +
                   "#$ -notify\n" +
                   "#$ -N " + job_name + "\n" +
                   "#$ -o " + stdout_file + "\n" +
                   "#$ -e " + stderror_file + "\n" +
                   "#$ -pe threads " + str(threads_num) + "\n\n")

    docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

    docker_image = obj['DROPSEQ_IMG']


    cmd_1 = ("TrimStartingSequence \\\n" +
             "    INPUT=" + input_file + " \\\n" +
             "    OUTPUT=" + output_file_adapter + " \\\n" +
             "    OUTPUT_SUMMARY=" + summary_file_adapter + " \\\n" +
             "    SEQUENCE=" + obj['TRIMSEQUENCE'] + " \\\n" +
             "    MISMATCHES=0 \\\n" +
             "    NUM_BASES=5")

    cmd_2 = ("PolyATrimmer \\\n" +
             "    INPUT=" + output_file_adapter + " \\\n" +
             "    OUTPUT=" + output_file_adapter_polyA + " \\\n" +
             "    OUTPUT_SUMMARY=" + summary_file_adapter_polyA + " \\\n" +
             "    MISMATCHES=0 \\\n" +
             "    NUM_BASES=5")

    sh_file = os.path.join(output_dir, sample_name + ".TrimDropseq.sh")

    with open(sh_file, mode="w") as fh:
        fh.write(qsub_option)
        fh.write(docker_run_option + " \\\n")
        fh.write(docker_image + " \\\n")
        fh.write(cmd_1 + "\n\n")
        fh.write(docker_run_option + " \\\n")
        fh.write(docker_image + " \\\n")
        fh.write(cmd_2)

    os.chmod(sh_file, 0755)

    list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
