#!/usr/bin/python3

import os
import re
import subprocess
import yaml

with open('makeref.yaml') as file:
    obj = yaml.safe_load(file)

# species which information are wanted to be combined
species = [obj['SPECIES'], 'ercc']

# input dir
genome_file = dict()
genome_file[obj['SPECIES']] = obj['INPUT_FASTA']
genome_file['ercc'] = obj['ERCC_FASTA']

annotation_file = dict()
annotation_file[obj['SPECIES']] = obj['INPUT_GTF']
annotation_file['ercc'] = obj['ERCC_GTF']

# output dir
output_dir = obj['REF_DIR']

## add
base_dir = os.getcwd()
ref_dir = os.path.join(obj['REF_DIR'], "STARindex")
genome_fasta = os.path.join(obj['REF_DIR'], "combined.fa")
gtf = os.path.join(obj['REF_DIR'], "combined.gtf")
picarddict = os.path.join(obj['REF_DIR'], "combined.dict")

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

output_genome_file = dict()
output_annotation_file = dict()
for sp in species:
    output_genome_file[sp] = os.path.join(output_dir, sp + "_conv.fa")
    output_annotation_file[sp] = os.path.join(output_dir, sp + "_conv.gtf")

output_genome_cat = os.path.join(output_dir, "combined.fa")
output_annotation_cat = os.path.join(output_dir, "combined.gtf")

if not os.path.isfile(output_genome_cat):
# conversion of chr name of genome.fa files
    for sp in species:
        f_input = open(genome_file[sp])
        f_output = open(output_genome_file[sp], 'w')

        for line in f_input:
            if line.startswith(">"):
                line = line.replace(">", ">" + sp + "_")
            f_output.write(line)

        f_input.close()
        f_output.close()
    cmd_genome = ("cat " + output_genome_file[species[0]] + " " +
              output_genome_file[species[1]] + " > " + output_genome_cat)
    subprocess.call(cmd_genome, shell=True)
    cmd_clean = ("rm *_conv.fa")

if not os.path.isfile(output_annotation_cat):
# conversion oRefr name of annotation.gtf files
    for sp in species:
        f_input = open(annotation_file[sp])
        f_output = open(output_annotation_file[sp], 'w')

        for line in f_input:
            if not line.startswith("#"):
                line = re.sub(r'^', sp + "_", line)
                f_output.write(line)

        f_input.close()
        f_output.close()
    cmd_annotation = ("cat " + output_annotation_file[species[0]] + " " +
                      output_annotation_file[species[1]] + " > " + output_annotation_cat)
    subprocess.call(cmd_annotation, shell=True)
    cmd_clean = ("rm *_conv.gtf")

## add
if not os.path.isdir(ref_dir):
    os.makedirs(ref_dir)

threads_num = obj['THREADNUM']

stdout_file = os.path.join(ref_dir, "qsub.o.txt")
stderror_file = os.path.join(ref_dir, "qsub.e.txt")

job_name = "GenRef"

qsub_option = ("#!/bin/bash\n\n" +
               "#$ -q " + obj['QUEUE_NODE'] + "\n" +
               "#$ -notify\n" +
               "#$ -N " + job_name + "\n" +
               "#$ -o " + stdout_file + "\n" +
               "#$ -e " + stderror_file + "\n" +
               "#$ -pe threads " + str(threads_num) + "\n\n")

docker_run_option = (obj['DOCKER_OPT'] + " --name ${USER}_" + job_name)

docker_image1 = obj['STAR_IMG']

cmd1 = ("STAR \\\n" +
       "--runMode genomeGenerate \\\n" +
       "--genomeDir " + ref_dir + " \\\n" +
       "--genomeFastaFiles " + genome_fasta + " \\\n" +
       "--sjdbGTFfile " + gtf + " \\\n" +
       "--sjdbOverhang 100 \\\n" +
       "--runThreadN 22")

docker_image2 = obj['PICARD_IMG']

cmd2 = ("java -Xmx64g -jar /usr/local/bin//picard.jar CreateSequenceDictionary \\\n" +
    "REFERENCE=" + genome_fasta + " \\\n" +
    "OUTPUT=" + picarddict )

sh_file = os.path.join(ref_dir, "GenerateIndex.sh")

with open(sh_file, mode="w") as fh:
    fh.write(qsub_option)
    fh.write(docker_run_option + " \\\n")
    fh.write(docker_image1 + " \\\n")
    fh.write(cmd1 + " \n\n")
    fh.write(docker_run_option + " \\\n")
    fh.write(docker_image2 + " \\\n")
    fh.write(cmd2)

os.chmod(sh_file, 0o755)

subprocess.call(obj["RUN_CMD"] + " " + sh_file, shell=True)
