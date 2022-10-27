#!/bin/sh
CURRENT_PATH="${PWD}"

GENEPJT="Gencode"
REF_VERSION="M27"
ASBLNAME="GRCm39"
SP_NAME0="mouse"

output_dir="${CURRENT_PATH}"

if [ ! -f ${output_dir}/${ASBLNAME}.primary_assembly.genome.fa ]; then
        wget -P ${output_dir} ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_${SP_NAME0}/release_${REF_VERSION}/${ASBLNAME}.primary_assembly.genome.fa.gz ;
        gunzip ${output_dir}/${ASBLNAME}.primary_assembly.genome.fa.gz ;
fi

if [ ! -f ${output_dir}/gencode.v${REF_VERSION}.primary_assembly.annotation.gtf ]; then
        wget -P ${output_dir} ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_${SP_NAME0}/release_${REF_VERSION}/gencode.v${REF_VERSION}.primary_assembly.annotation.gtf.gz ;
        gunzip ${output_dir}/gencode.v${REF_VERSION}.primary_assembly.annotation.gtf.gz ;
fi

