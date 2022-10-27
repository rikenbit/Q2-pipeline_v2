#!/bin/bash

function qsubwait {
  while [[ $(qstat -u $USER | wc -l ) != 0 ]]
  do
    sleep $1
  done
}

QSUBLIST="LIST${1:-1}"
LIST1="01_bcl2fastq \
       02_FastQC"
LIST2="03_1_Downsampling_several_name_size \
       04_FastQC_ds"
LIST3="05_FastxTrimmer \
       06_FastqToSam \
       07_TagBamWithReadSequenceExtended \
       08_TrimDropseq \
       09_SamToFastq \
       10_STAR \
       11_SortSam \
       12_MergeBamAlignment \
       13_TagReadWithGeneFunction \
       14_correct_barcode \
       15_BamTagHistogram \
       16_DigitalExpression \
       17_analog_expression"

for index in ${!QSUBLIST}
do
  ./${index}_qsub.py
  echo "$(date -u "+%Y/%m/%d %H:%M:%S") ${index}_qsub.py submitted"
  qsubwait 10s
  echo "$(date -u "+%Y/%m/%d %H:%M:%S") ${index}_qsub.py finished"
  printf "\n\n"
  # waiting for exec nodes to be deallocated
  #sleep 10m
done
