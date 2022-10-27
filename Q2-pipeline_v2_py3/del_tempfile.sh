#!/bin/bash
DEL_LOG_DIR="Log"
if [ ! -d ${DEL_LOG_DIR} ]; then
        mkdir -p ${DEL_LOG_DIR}
fi

rm -fv ./results/05_fastx_trimmer/*.fastq.gz >& ${DEL_LOG_DIR}/del_05_fastx_trimmer1.log

rm -fv ./results/06_FastqToSam/*.bam >& ${DEL_LOG_DIR}/del_06_FastqToSam1.log

rm -fv ./results/07_TagBamWithReadSequenceExtended/*.bam >& ${DEL_LOG_DIR}/del_07_TagBamWithReadSequenceExtended1.log

rm -fv ./results/11_SortSam/*.bam >& ${DEL_LOG_DIR}/del_11_SortSam1.log

rm -fv ./results/12_MergeBamAlignment/*.bam >& ${DEL_LOG_DIR}/del_12_MergeBamAlignment1.log

rm -fv ./results/13_TagReadWithGeneFunction/*.bam >& ${DEL_LOG_DIR}/del_13_TagReadWithGeneFunction1

rm -fv ./results/10_STAR/*.bam >& ${DEL_LOG_DIR}/del_10_STAR1.log

