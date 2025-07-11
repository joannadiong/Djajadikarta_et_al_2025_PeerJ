********** NOTES ********** 

** Author: Joanna Diong
** Date: 29 January 2021

** This do file analyses data on secondary outcomes from the randomised 
** controlled trial of step training on falls in people with MS.

** Data from Spike files were processed in Python, and cleaned data are
** analysed in Stata.


********** PRELIMINARIES ********** 

version 16
clear all
clear matrix
drop _all
capture log close

  ** Settings.

set more off
set scheme lean3
pause on

  ** LINUX: Enter name of root directory and name of this do file.

local pathname = `""/home/joanna/Dropbox/Projects/proprioRCT/src/code/stats/""'
local dofilename = `""script.do""'

  ** Open a time- and date-stamped log file and copy a time- and date-stamped
  ** do file and data file to the log file directory.

local pathandnameofdofile = `"""' + `pathname' + `dofilename' + `"""'
local pathoflogfilesname = `"""' + `pathname' + "log-files/" + `"""'
local pathofdatafilesname = `"""' + `pathname' + "data/" + `"""'
local pathofgraphfilesname = `"""' + `pathname' + "graphs/" + `"""'
local cdate = "c(current_date)"
local ctime = "c(current_time)"
local ctime = subinstr(`ctime',":","h",1)
local ctime = subinstr("`ctime'",":","m",1)
local logfilename = `"""' + "log " + `cdate' + " " + "`ctime'" + "s.log" + `"""'
local backupdofilename = `"""' + "do " + `cdate' + " " + "`ctime'" + "s.txt" + `"""'
cd `pathoflogfilesname'
*log using `logfilename'
*copy `pathandnameofdofile' `backupdofilename'


********** COMBINE DATASETS, TIDY UP **********

cd `pathofdatafilesname'

drop _all
insheet using "data_recov.csv", clear
drop group_unblind
quietly gen mid = _n
move mid id
save recovery.dta, replace

drop _all
import excel "proprio_funct_covar_measures.xlsx", firstrow
drop if id==18 /* Sub 18 withdrew from study: withdraw data */
quietly gen mid = _n
move mid id
save function.dta, replace

use function.dta, clear
merge 1:1 mid using recovery

/*Note: variables torque, va, twitch are values at 15 s, 
sampled from repeated measures from time to recovery data.
Variable n_* is the normalised value at 15 s, obtained from polynomial function.
These variables and time are not used in the final analysis and so are removed.
*/
drop v1 time n_* L M N O P

foreach var of varlist torque va twitch reaction_time detect_thresh total_sway_foam speed_10mwt dist_6mwt step_time {
    quietly destring `var', replace    
}

label define labGroup 0 "con" 1 "trt"
label values group labGroup
label define labSession 0 "pre" 1 "pos"
label values session labSession

* fix group codes after unblinding of analysis
gen group_unblind = .
replace group_unblind = 1 if group == 0
replace group_unblind = 0 if group == 1
move group_unblind group
sort group_unblind mid
drop group
rename group_unblind group
label values group labGroup
sort group id mid

save data_final.dta, replace
outsheet using data_final.csv, comma nolabel replace


********** ANALYSE OUTCOMES **********

  ** Survival analysis for time to recovery outcomes

foreach var of varlist rt_torque rt_twitch rt_va { 
     
    display _n _n "SURVIVAL ANALYSIS OF: " "`var'"
    display _n

    preserve
      quietly gen time1 = `var'

      * Create failure event
      gen recovered = 0
      replace recovered = 1 if time1 != .
	  
	  * set failure event as missing if subject was not tested
	  if `var' == rt_torque {
	  	replace recovered = . if torque == . 
	  }
	  if `var' == rt_twitch {
	  	replace recovered = . if twitch == . 
	  }
	  if `var' == rt_va {
	  	replace recovered = . if va == . 
	  }
      
      /* Fix time variable. 
      For subjects who fail at entry to study (i.e. recovered at 15 s), 
      set recovery to at 15.1 s as Stata time span is defined as [t0,t1)——or as t0 <= t < t1
      https://www.stata.com/support/faqs/statistics/time-and-cox-model/ 
      */
      replace time1 = 15.1 if time1 == 15
	  
	  * set longest observed time as 120, and as missing if subject was not tested
	  if `var' == rt_torque {
	  	replace time1 = 120 if time1 == . & torque != . 
	  }
	  if `var' == rt_twitch {
	  	replace time1 = 120 if time1 == . & twitch != . 
	  }
	  if `var' == rt_va {
	  	replace time1 = 120 if time1 == . & va != . 
	  }
	  
      * declare survival data: treat each panel row as a single subject to include censoring
      stset time1, id(mid) failure(recovered) 
      
      list id group session time1 recovered _t0 _t _d _st if id<=3 | id>=64, noobs sepby(id)
      sts list, by(group session)
      stdescribe
      
      * graph
      cd `pathofgraphfilesname'
      sts graph, by(group session) censored(number) /// 
        risktable(, order(1 "Control pre" 2 "Control post" 3 "Treated pre" 4 "Treated post") failevents) /// 
        legend(label(1 "Control pre") label(2 "Control post") label(3 "Treated pre") label(4 "Treated post"))      
      graph save survival, replace
      graph export survival_`var'.tif, width(1200) height(900) replace
      
      sts graph, by(group session) cumhaz censored(number) /// 
        risktable(, order(1 "Control pre" 2 "Control post" 3 "Treated pre" 4 "Treated post") failevents) /// 
        legend(label(1 "Control pre") label(2 "Control post") label(3 "Treated pre") label(4 "Treated post"))      
      graph save cumhaz, replace
      graph export cumhaz_`var'.tif, width(1200) height(900) replace
      
      * Primary analysis: parametric, with subject id as random intercept
      xtset id
      mestreg group session || id:, distribution(weibull)   
      
      graph drop Graph
    
    restore
    
}


  ** Robust regression for all other outcomes

foreach var of varlist edss ipeq { 
    
    display _n _n "SUMMARY STATISTICS OF: " "`var'"
    bysort group session: summarize `var'
    
}

replace speed_10mwt = 10 / speed_10mwt 
replace step_time = step_time / (60 * 60)  /* in hours */

* Rescale adherence from units of hours to proportion of total:
* total exercise time is 6 months = 52/2 weeks of 120 min = 2 hrs per week
replace step_time = step_time / (52 / 2 * 2)

foreach var of varlist bv_torque bv_twitch bv_va /// 
                       fv_torque fv_twitch fv_va /// 
                       detect_thresh reaction_time /// 
                       total_sway_foam speed_10mwt dist_6mwt { 
    
    display _n _n "ROBUST REGRESSION OF: " "`var'"
    bysort group session: summarize `var'
    
    preserve 
      keep `var' id group session edss ipeq step_time
      reshape wide `var', i(id) j(session)
      
      rreg `var'1 group `var'0 
      
      ivregress 2sls `var'1 `var'0 (step_time = group) 
    
    restore
    
}



********** END **********

*log close
exit

