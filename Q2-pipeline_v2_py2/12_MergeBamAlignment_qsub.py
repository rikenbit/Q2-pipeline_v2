#!/usr/bin/python2

import os
import glob
import subprocess
import yaml

with open('configure.yaml') as file:
    obj = yaml.safe_load(file)

base_dir = os.getcwd()
input_dir = os.path.join(base_dir, "results", "11_SortSam")
aligned_bam_dir = input_dir
unmapped_bam_dir = os.path.join(base_dir, "results", "08_TrimDropseq")
output_dir = os.path.join(base_dir, "results", "12_MergeBamAlignment")

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

species = (obj['SPECIES'], )

reference_seq = dict()
reference_seq[obj['SPECIES']] = (obj['REF_DIR'] + "/combined.fa")

list_sh_file = []

threads_num = obj['THREADNUM']

for sp in species:

    input_files = glob.glob(os.path.join(input_dir, "*_" + sp + "_sorted.bam"))

    for i, input_file in enumerate(input_files):

        sample_name = (os.path.split(input_file)[1].split(".")[0].
                       replace("_" + sp + "_sorted", ""))
        unmapped_bam = os.path.join(unmapped_bam_dir,
                                    sample_name + "_trim_adapter_polyA.bam")
        aligned_bam = os.path.join(aligned_bam_dir,
                                   sample_name + "_" + sp + "_sorted.bam")
        output_file = os.path.join(output_dir,
                                   sample_name + "_" + sp + "_merged.bam")
        stdout_file = os.path.join(output_dir, sample_name + ".o.txt")
        stderror_file = os.path.join(output_dir, sample_name + ".e.txt")

        job_name = "MergBa_" + str(i) + "_" + sp

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
               "    -jar /usr/local/bin/picard.jar MergeBamAlignment \\\n" +
               "    REFERENCE_SEQUENCE=" + reference_seq[sp] + " \\\n" +
               "    UNMAPPED_BAM=" + unmapped_bam + " \\\n" +
               "    ALIGNED_BAM=" + aligned_bam + " \\\n" +
               "    OUTPUT=" + output_file + " \\\n" +
               "    INCLUDE_SECONDARY_ALIGNMENTS=false \\\n" +
               "    PAIRED_RUN=false \\\n" +
               "    TMP_DIR=" + output_dir + " \\\n" +
               "    ")

        sh_file = os.path.join(output_dir,
                               sample_name + ".MergeBamAlignment.sh")

        with open(sh_file, mode="w") as fh:
            fh.write(qsub_option)
            fh.write(docker_run_option + " \\\n")
            fh.write(docker_image + " \\\n")
            fh.write(cmd)

        os.chmod(sh_file, 0755)

        list_sh_file.append(sh_file)

for sh_file in list_sh_file:
    subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
