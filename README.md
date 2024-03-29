This repository contains scripts for identification and analysis of active mobile genetic elements (MGEs) in bacterial genomes. 
# Installation

To use the script it is required to obtain EDirect software and your NCBI API key. To install EDirect (see see https://dataguide.nlm.nih.gov/edirect/install.html for more details):

```bash
cd ~
/bin/bash
perl -MNet::FTP -e \
    '$ftp = new Net::FTP("ftp.ncbi.nlm.nih.gov", Passive => 1);
    $ftp->login; $ftp->binary;
    $ftp->get("/entrez/entrezdirect/edirect.tar.gz");'
gunzip -c edirect.tar.gz | tar xf -
rm edirect.tar.gz
builtin exit
export PATH=$PATH:$HOME/edirect >& /dev/null || setenv PATH "${PATH}:$HOME/edirect"
./edirect/setup.sh
```


For obtaining your NCBI API key see https://support.nlm.nih.gov/knowledgebase/article/KA-05317/en-us.
Use conda to install all required packages and dependencies.  For conda installation procedure see https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html.

First you clone the github repository or download and unzip it from this page.
```bash
git clone https://github.com/smyshlya/MGEtools.git
```
Now setting up the environment...
```bash
cd MGEtools/
conda env create -f MGEtools.yml
conda activate HTrate
```
...and it's ready to use! eg
```bash
python HTrate.py --api_key YOUR_API_KEY HTrate_example.txt
```

# HTrate

A python script to identify HTed proteins and analyse their distribution. HTed proteins are the proteins that are present in unrelated bacteria (same protein sequence exists in different genera) and therefore are putatively horizontally transferred. 
It takes protein NCBI accession numbers (provided in the input file, see HTrate_example.txt), creates Identical Protein (IP) record files for each of the accession numbers 
(stored in the "/ip" folder), and outputs an /ip/out.csv file with distribution of all horizontally transferred proteins and HTrate_result.svg image file showing the distribution plot.


Running time for a dataset with ~35K protein accession numbers is approximately 15h on iMac.

## Usage
```bash
usage: HTrate.py [-h] [--ht HT] [--n N] [--api_key API_KEY] file

positional arguments:
  file               input file with the list of NCBI protein accession numbers 

optional arguments:
  -h, --help         show this help message and exit
  --ht HT            threshold number of different genera for HT detection (2 is default)
  --n N              number of proteins to retrieve from the input file; if 0 retrieves all of them (0 is default)
  --api_key API_KEY  this is your api_key to access NCBI (see https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/) and download IP records (none is deafult, i am not sure if that works)

```
# HTdate
HTdate.py is developed to retrieve additional metadata, such as isolation date, host and geographic location of the strain where the copy was identified for all MGE copies

# find_all_copies
To retrieve the full copies of an element the script find_all_copies.py was developed, which requires information on the left and right transposon end sequences to automatically extract all copies of MGE of interest.  The script then creates a file with all protein sequences encoded between determined RE and LE.

```bash
usage: find_all_copies.py [-h] [--a A] [--s S] [--api_key API_KEY] file

positional arguments:
  file               This is the input file

optional arguments:
  -h, --help         show this help message and exit
  --a A              create alignment of nucleotide sequences
  --s S              nucleotide sequences are expanded by this length for the alignment
  --api_key API_KEY  This is your api_key to access NCBI
```