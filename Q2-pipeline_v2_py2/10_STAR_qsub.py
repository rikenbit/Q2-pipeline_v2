#!/usr/bin/python2

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

# directoris
base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "09_SamToFastq")
output_dir = os.path.join(base_dir, "results", "10_STAR")

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

species = (obj['SPECIES'], )

genome_dir = dict()
genome_dir[obj['SPECIES']] = (obj['REF_DIR'] + "/STARindex")

# make sh files
input_files = glob.glob(os.path.join(input_dir, "*.fastq"))
list_sh_file = []

threads_num = obj['THREADNUM']

for i, input_file in enumerate(input_files):
    sample_name = os.path.split(input_file)[1].split(".")[0].replace(
        "_trim_adapter_polyA", "")

    for sp in species:
        output_file_prefix = os.path.join(output_dir,
                                          sample_name + "_" + sp + "_STAR.")
        stdout_file = os.path.join(output_dir,
                                   sample_name + "_" + sp + ".o.txt")
        stderror_file = os.path.join(output_dir,
                                     sample_name + "_" + sp + ".e.txt")
        job_name = "STAR_" + str(i) + "_" + sp

        qsub_option = ("#!/bin/bash\n\n" +
                       "#$ -q " + obj['QUEUE_NODE'] + "\n" +
                       "#$ -notify\n" +
                       "#$ -N " + job_name + "\n" +
                       "#$ -o " + stdout_file + "\n" +
                       "#$ -e " + stderror_file + "\n" +
                       "#$ -pe threads " + str(threads_num) + "\n\n")

        docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

        docker_image = obj['STAR_IMG']

        cmd = ("STAR --runThreadN " + obj['THREADNUM'] + " --genomeDir " + genome_dir[sp] + " --readFilesIn " + input_file + " --outFileNamePrefix " + output_file_prefix )

        sh_file = os.path.join(output_dir, sample_name + "_" + sp + ".STAR.sh")

        with open(sh_file, mode="w") as fh:
            fh.write(qsub_option)
            fh.write(docker_run_option + " \\\n")
            fh.write(docker_image + " \\\n")
            fh.write(cmd)

        os.chmod(sh_file, 0755)

        list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)

