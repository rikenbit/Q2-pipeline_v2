#!/usr/bin/python3

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "14_CorrectBarcode")
output_dir = os.path.join(base_dir, "results", "17_AnalogExpression")

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

program_path = os.path.join(base_dir, "analog_expression_v2.py")
barcode_file = os.path.join(base_dir, obj['BARCODE_FILE'])

gtf_dict = dict()
gtf_dict[obj['SPECIES']] = obj['REF_DIR'] + "/combined.gtf"
input_files = glob.glob(os.path.join(input_dir, "*.bam"))

list_sh_file = []

threads_num = obj['THREADNUM']

for i, input_file in enumerate(input_files):

    sample_name = os.path.split(input_file)[1].split(".")[0]

    count_found = 0

    for sp in [obj['SPECIES'], ]:
        if sp in sample_name:
            count_found += 1
            gtf_file = gtf_dict[sp]

    if count_found != 1:
        raise Exception("GTF file could not be identified")

    output_file = os.path.join(output_dir,
                               sample_name + "_age.txt")

    stdout_file = output_file.replace("_age.txt", ".o.txt")
    stderror_file = output_file.replace("_age.txt", ".e.txt")

    job_name = "AnaExp" + str(i)

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
           "-g " + gtf_file + " \\\n" +
           "-o " + output_file + " \\\n" +
           "")

    sh_file = output_file.replace("_age.txt", ".sh")

    with open(sh_file, mode="w") as fh:
        fh.write(qsub_option)
        fh.write(docker_run_option + " \\\n")
        fh.write(docker_image + " \\\n")
        fh.write(cmd)
        os.chmod(sh_file, 0o755)

    list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
