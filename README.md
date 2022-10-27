# Quartz-Seq2 pipeline version2
The repository provides a data analysis workflow for Quartz-Seq2, one of the high-throughput single-cell RNA-seq methods. This workflow produces a gene expression/UMI count matrix from fastq/bcl files.

## System Requirements

- git (or wget, curl)
- docker 
- python
  - pyyaml
- grid engine



## Installation and settings

### Before you begin

Install grid engein.

Install [Docker](https://docs.docker.com/engine/installation/) for full pipeline reproducibility.

### Setup

#### Download scripts

Clone from github.

```bash
git clone rikenbit/Q2-pipeline_v2
```

or download script with wget/curl and uncompress it.

```
wget https://github.com/rikenbit/Q2-pipeline_v2/releases/download/1.0/Q2-pipeline_v2_py2.tar.gz
or
curl -o https://github.com/rikenbit/Q2-pipeline_v2/releases/download/1.0/Q2-pipeline_v2_py2.tar.gz

tar xf Q2-pipeline_v2_py2.tar.gz
```

Change directories to the following:Q2-pipeline_v2.

```
cd Q2-pipeline_v2_py2
```

#### Edit Permission

Sets the execute permission for the file.

```bash
chmod +x *.py
chmod +x *.sh
```

#### Pull docker container or build dockerfiles

```bash
docker pull myoshimura080822/bcl2fastq2:2.0
docker pull biocontainers/fastqc:v0.11.9_cv8
docker pull itpsc/seqtk:1.3
docker pull itpsc/fastx_toolkit:0.0.14
docker pull itpsc/picard:2.25.2
docker pull itpsc/dropseq-tools:2.4.0
docker pull itpsc/py2-pyper:1.1.2
docker pull itpsc/star:2.7.8a
```



### Preparation of Reference data

#### Get Genome data fasta/gtf

In advance, Get fasta / gtf.
For samples, refer "./reference/Download_Gencode_mouse.sh".
Below is an example script for download mouse reference data from [Gencode](https://www.gencodegenes.org/).

```bash
sh Download_Gencode_mouse.sh
```



#### Edit makeref.yaml

Enter downloaded file path to following field in the makeref.yaml.

- INPUT_FASTA: fasta file
- INPUT_GTF: gtf file

```yaml
# Gridengin queue name
QUEUE_NODE: 'all.q'
# Number of core
THREADNUM: '12'
# job scheduler command
RUN_CMD: 'qsub'
# Container OPTION
DOCKER_OPT: 'docker run --rm --init -u `id -u`:`id -g` -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro -v $HOME:$HOME -w $PWD'

# Container name
PICARD_IMG: 'itpsc/picard:2.25.2'
STAR_IMG: 'itpsc/star:2.7.8a'

SPECIES: 'mouse'

INPUT_FASTA: "./combined_mouse_Gencode_GRCm39_M26/GRCm39.primary_assembly.genome.fa"
INPUT_GTF: "./combined_mouse_Gencode_GRCm39_M26/gencode.vM26.primary_assembly.annotation.gtf"
ERCC_FASTA: "./ERCC/ERCC.fa"
ERCC_GTF: "./ERCC/ERCC.gtf"
REF_DIR: "./combined_mouse_Gencode_GRCm39_M26"
```

#### Run python script to build reference data

```bash
python make_reference.py
```

If it ends normally, the following files will be created under the specified directory.

```
.
├── STARindex
│   ├── GenerateStarIndex.sh
│   ├── Genome
│   ├── Log.out
│   ├── SA
│   ├── SAindex
│   ├── chrLength.txt
│   ├── chrName.txt
│   ├── chrNameLength.txt
│   ├── chrStart.txt
│   ├── exonGeTrInfo.tab
│   ├── exonInfo.tab
│   ├── geneInfo.tab
│   ├── genomeParameters.txt
│   ├── qsub.e.txt
│   ├── qsub.o.txt
│   ├── sjdbInfo.txt
│   ├── sjdbList.fromGTF.out.tab
│   ├── sjdbList.out.tab
│   └── transcriptInfo.tab
├── combined.dict
├── combined.fa
├── combined.gtf
```



#### Edit configure.yaml

Specify the directory of the created reference data in REF_DIR.

```yaml
# Gridengin queue name
QUEUE_NODE: 'all.q'
# Number of core
THREADNUM: '12'
# job scheduler command
RUN_CMD: 'qsub'
# Container OPTION
DOCKER_OPT: 'docker run --rm --init -u `id -u`:`id -g` -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro -v $HOME:$HOME -w $PWD'

# Container name
BCL2FASTQ2_IMG: 'myoshimura080822/bcl2fastq2:2.0'
FASTQC_IMG: 'biocontainers/fastqc:v0.11.9_cv8'
SEQTK_IMG: 'itpsc/seqtk:1.3'
FASTX_TOOLKIT_IMG: 'itpsc/fastx_toolkit:0.0.14'
PICARD_IMG: 'itpsc/picard:2.25.2'
DROPSEQ_IMG: 'itpsc/dropseq-tools:2.4.0'
PYPER_IMG: 'itpsc/py2-pyper:1.1.2'
STAR_IMG: 'itpsc/star:2.7.8a'

# Reference file
BCL_DIR: '/data/*****'
SAMPLESHEET: 'SampleSheet.csv'
REF_DIR: './combined_mouse_Gencode_M26'
SPECIES: 'mouse'
CB_LENGTH: '15'
# Cell Barcode length 14mer or 15mer
BARCODE_FILE: 'CB_15mer_384_SetA.txt'
TRIMSEQUENCE: 'GTATAGAATTCGCGGCCGCTCGCGAT'
```



## Usage

### Pipeline Execution

#### Conversion of bcl

Conversion bcl to fastq, and run FastQC.

```bash
sh 00_pipeline.sh 1
```



#### Downsampling of data set

```bash
sh 00_pipeline.sh 2
```



#### Run all remaining pipelines

```bash
sh 00_pipeline.sh 3
```

As the process progresses, the message "~ _qsub.py finished" will be displayed.
The script will end when it completes up to 17_analog_expression.
Make sure that it is not terminated due to an error and that there are no jobs left, and if there are no problems, it is complete.



If you want to run the pipeline manually, run the python scripts sequentially.

```bash
python 01_bcl2fastq
```

Execute sequentially up to 17_analog_expression.



#### Delete intermediate data

Delete the intermediate file when all python scripts are finished.

```
sh data_copy.sh
```

#### Aggregate copy of files used for secondary analysis

```bash
sh del_tempfile.sh
```

When you run the script, the following files will be copied to directory.

- FastQC
- BAMTagHistogram
- DigitalExpression
- AnalogExpression
- STAR Log file

```
Analysis_results
.
├── 02_fastqc
│   ├──${SAMPLE}_I1_001.e.txt
│   ├──${SAMPLE}_I1_001.fastqc.sh
│   ├──${SAMPLE}_I1_001.o.txt
│   ├──${SAMPLE}_I1_001_fastqc.html
│   ├──${SAMPLE}_I1_001_fastqc.zip
│   ├──${SAMPLE}_R1_001.e.txt
│   ├──${SAMPLE}_R1_001.fastqc.sh
│   ├──${SAMPLE}_R1_001.o.txt
│   ├──${SAMPLE}_R1_001_fastqc.html
│   ├──${SAMPLE}_R1_001_fastqc.zip
│   ├──${SAMPLE}_R2_001.e.txt
│   ├──${SAMPLE}_R2_001.fastqc.sh
│   ├──${SAMPLE}_R2_001.o.txt
│   ├──${SAMPLE}_R2_001_fastqc.html
│   └──${SAMPLE}_R2_001_fastqc.zip
├──${SAMPLE}_ds384_***_seqlev_d2_XC_readcounts.txt.gz
├──${SAMPLE}_ds384_***_seqlev_d2_age.txt
├──${SAMPLE}_ds384_***_seqlev_d2_dge.txt.gz
├──${SAMPLE}_ds384_***_STAR.Log.final.out
```

*${SAMPLE} indicates sample name.



## License

Copyright (c) RIKEN Bioinformatics Research Unit Released under the MIT license (http://www.opensource.org/licenses/mit-license.php)

