## Title

Proprioception and muscle performance unchanged by in-home step training in multiple sclerosis: secondary outcomes analysis

Zoë J Djajadikarta<sup>1</sup>, Siobhan C Dongés<sup>1</sup>, Joanna Diong<sup>1,2</sup>, Phu D Hoang<sup>1,3</sup>, David S Kennedy<sup>1,4,5</sup>, Jasmine C Menant<sup>1,3</sup>, Stephen R Lord<sup>1,3</sup>, Janet L Taylor<sup>1,6</sup>, Simon C Gandevia<sup>1,3</sup>

1. Neuroscience Research Australia, Sydney, NSW, Australia
2. School of Medical Sciences, Faculty of Medicine and Health, The University of Sydney, Sydney, NSW, Australia
3. University of New South Wales, Sydney, Australia
4. Graduate School of Health, Physiotherapy, University of Technology Sydney
5. Motion and Mobility Research laboratory, University of Victoria, Victoria, Canada
6. Edith Cowan University, Joondalup, Perth, WA, Australia

## Suggested citation

Djajadikarta ZJ, Dongés SC, Diong J, Hoang PD, Kennedy DS, Menant JC, Lord SR, Taylor JL, Gandevia SC (2025) Proprioception and muscle performance unchanged by in-home step training in multiple sclerosis: secondary outcomes analysis. PeerJ. 

## Data

Raw data files in **data/raw/**:

* _allmotor_long.xlsx_: motor performance outcomes during time to recovery after fatigue 
* _proprio_funct_covar_measures.xlsx_: proprioception, functional, and covariate outcomes 

## Code

The Python script calls _allmotor_long.xlsx_ to generate time to recovery data _data_recov.csv_. It outputs the cleaned dataset _data.csv_

The Stata script calls Python-generated _data_recov.csv_ and raw data _proprio_funct_covar_measures.xlsx_, merges them and outputs the cleaned final dataset _data_final.csv_

Run Python script, then run Stata script. 

Code files were written by Joanna Diong (Python v3.11, Stata v18). 

### Python

Python code is run in the virtual environment _env_, which contains the requirements. A _requirements.txt_ file is retained in the main repo. 

Activate the environment with:

`source env/bin/activate`

Deactivate the environment with: 

`deactivate`

Code files in **bin/**:

* _proc.py_: process file with functions 
* _script.py_: script file to process time to recovery data

### Running Python code

In _proc.py_ line 18, file path is set to current directory; update as required.

Run _script.py_

### Stata

Code files in **bin/**:

* _script.do_: script to merge Python-generated and raw datasets, and perform all statistical analyses
  * Survival analysis of time to recovery outcomes
  * Robust regression of all outcomes
  * Complier average causal effects (CACE) analysis of all outcomes using instrumental variable regression

### Running Stata code

In _script.do_ lines 29 and 30, set file paths for project and DO file to current directory.

Paths are currently set for Linux or Mac operating systems using forward slashes `/`. 
They will need to be updated for Windows using backward slashes `\`, 
or for different project locations on different machines. 

Place graph scheme _scheme-lean3.scheme_ in Stata's **ado/base/s/**.

Uncomment lines 47, 48, 248 to save a log file in **data/proc/**.

Run _script.do_

