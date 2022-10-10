## Title

A home-based step-training intervention did not change ankle proprioception and muscle performance in people with multiple sclerosis: Exploring secondary outcomes from a randomised controlled trial

Zoë J Djajadikarta^1^, Siobhan C Dongés^1^, Joanna Diong^1,2^, Phu D Hoang^1,3^, David S Kennedy^4^, Stephen R Lord^1,5^, Janet L Taylor^6^, Simon C Gandevia^1,5^

1. Neuroscience Research Australia, Sydney, NSW, Australia
2. School of Medical Sciences, Faculty of Medicine and Health, The University of Sydney, Sydney, NSW, Australia
3. Multiple Sclerosis (MS) Australia, Sydney, NSW, Australia
4. Graduate School of Health, Physiotherapy, University of Technology Sydney
5. University of New South Wales, Sydney, Australia
6. Edith Cowan University, Joondalup, Perth, WA, Australia

## Suggested citation

Djajadikarta ZJ, Dongés SC, Diong J, Hoang PD, Kennedy DS, Lord SR, Taylor JL, Gandevia SC (2022)  A home-based step-training intervention did not change ankle proprioception and muscle performance in people with multiple sclerosis: Exploring secondary outcomes from a randomised controlled trial. **[ADD JOURNAL]**

## Data

Raw data files in **data/raw/**:

* _allmotor_long.xlsx_: motor performance outcomes during time to recovery after fatigue 
* _proprio_funct_covar_measures.xlsx_: proprioception, functional, and covariate outcomes 

## Code

The Python script calls _allmotor_long.xlsx_ to generate time to recovery data _data_recov.csv_. It outputs the cleaned dataset _data.csv_

The Stata script calls Python-generated _data_recov.csv_ and raw data _proprio_funct_covar_measures.xlsx_, merges them and outputs the cleaned final dataset _data_final.csv_

Run Python script, then run Stata script. 

Code files were written by Joanna Diong (Python v3.8, Stata v16). 

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

In _proc.py_ line 18, set file path to local directory

Run _script.py_

### Stata

Code files in **bin/**:

* _script.do_: script to merge Python-generated and raw datasets, and perform all statistical analyses
  * Survival analysis of time to recovery outcomes
  * Robust regression of all outcomes
  * Complier average causal effects (CACE) analysis of all outcomes using instrumental variable regression

### Running Stata code

In _script.do_ lines 31-34, set file paths to local directory.

Paths are currently set for Linux operating system. They will need to be updated for Windows, or for different project locations on different machines. 

Place graph scheme _scheme-lean3.scheme_ in Stata's **ado/base/s/**

Uncomment lines 49, 50, 241 to save a log file in **data/proc/**.

Run _script.do_

