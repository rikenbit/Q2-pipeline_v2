#!/usr/bin/python3

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

# directoris
base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "12_MergeBamAlignment")
output_dir = os.path.join(base_dir, "results", "13_TagReadWithGeneFunction")

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

species = (obj['SPECIES'], )

annotations_file = dict()
annotations_file[obj['SPECIES']] = (obj['REF_DIR'] + "/combined.gtf")

# make sh files
input_files = glob.glob(os.path.join(input_dir, "*_merged.bam"))
list_sh_file = []

threads_num = obj['THREADNUM']

for i, input_file in enumerate(input_files):
    for sp in species:
        sample_name = os.path.split(input_file)[1].split(".")[0].replace(
            "_merged", "")

        output_file = os.path.join(output_dir,
                                   sample_name + "_" + sp + "_gene_exon.bam")
        stdout_file = os.path.join(output_dir,
                                   sample_name + "_" + sp + ".o.txt")
        stderror_file = os.path.join(output_dir,
                                     sample_name + "_" + sp + ".e.txt")
        job_name = "TagGE" + str(i) + sp

        qsub_option = ("#!/bin/bash\n\n" +
                       "#$ -q " + obj['QUEUE_NODE'] + "\n" +
                       "#$ -notify\n" +
                       "#$ -N " + job_name + "\n" +
                       "#$ -o " + stdout_file + "\n" +
                       "#$ -e " + stderror_file + "\n" +
                       "#$ -pe threads " + str(threads_num) + "\n\n")

        docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

        docker_image = obj['DROPSEQ_IMG']

        cmd = ("TagReadWithGeneFunction \\\n" +
               "    I=" + input_file + " \\\n" +
               "    O=" + output_file + " \\\n" +
               "    ANNOTATIONS_FILE=" + annotations_file[sp] + " \\\n" +
#               "    TAG=GE \\\n" +
               "    ")

        sh_file = os.path.join(output_dir, sample_name + "_" +
                               sp + ".TagReadWithGeneFunction.sh")

        with open(sh_file, mode="w") as fh:
            fh.write(qsub_option)
            fh.write(docker_run_option + " \\\n")
            fh.write(docker_image + " \\\n")
            fh.write(cmd)
        os.chmod(sh_file, 0o755)

        list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
