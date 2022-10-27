#!/bin/bash
data_copy_dir="Analysis_results"
if [ ! -d ${data_copy_dir} ]; then
        mkdir -p ${data_copy_dir}
fi

cp -r ./results/02_fastqc ${data_copy_dir}
cp ./results/10_STAR/*.Log.final.out ${data_copy_dir}
cp ./results/15_BamTagHistogram/*XC_readcounts.txt.gz ${data_copy_dir}
cp ./results/16_DigitalExpression/*_dge.txt.gz ${data_copy_dir}
cp ./results/17_AnalogExpression/*_age.txt ${data_copy_dir}

