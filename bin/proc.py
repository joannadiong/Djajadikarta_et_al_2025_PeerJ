import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

matplotlib.rcParams.update({'font.size': 5})

# Test in console
# varname = 'va'
# id = 24
# order = 3
# sessionNum = 0
# session = 'pre'

def gen_data():
    path = Path('/home/joanna/Dropbox/Projects/proprioRCT')
    path_raw = path / 'data' / 'raw'
    path_proc = path / 'data' / 'proc'
    file = 'allmotor_long.xlsx'
    df = pd.read_excel(path_raw / file, na_values='.')
    df = df.rename(columns={'ID': 'id', 'Time': 'time'})
    df = df.drop(df[df['id'] == 18].index)  # sub 18 withdrew from study: withdraw data

    # create unblinded group codes unblinding of analysis
    # plot using unblinded codes but store blinded codes in exported CSV file
    # Stata file combines recovery and function data, and fixes group codes after unblinding
    df['group_unblind'] = 0
    df['group_unblind'] = np.where(df['group'] == 0, 1, 0) # where True, yield 1, otherwise yield 0

    return df, path_proc

def process_data(df, path_proc, plot=True):
    id_list = df.id.unique()
    df = _set_negative_va_to_zero(df)
    df = _set_va_over_100_to_100(df)
    varlist = ['torque', 'va', 'twitch']
    for varname in varlist:
        _gen_id_dir(id_list)
        df = _normalise_to_baseline(df, id_list, varname)
        df = _fit_data_by_id(df, id_list, varname, path_proc, plot=plot)
        if plot:
            _plot_data_all(df, id_list, varname, path_proc)
    return df

def write_to_csv(df, path_proc):
    # write all variables
    df.to_csv(path_proc / 'data.csv')

    # write recovery data: sample every 7th row, to get value at 15 s and time to recovery values
    d = df.iloc[2::7, :]
    d.to_csv(path_proc / 'data_recov.csv')


# ----------------------------------------------------------------------------------------------------------------------
# Hidden functions
# ----------------------------------------------------------------------------------------------------------------------
def _gen_id_dir(id_list: list):
    """Create subject folders for processed data"""
    for id in id_list:
        if not os.path.exists(os.path.join('..', '..', '..', 'data', 'proc', 'sub' + str(id))):
            os.mkdir(os.path.join('..', '..', '..', 'data', 'proc', 'sub' + str(id)))

def _set_negative_va_to_zero(df: pd.DataFrame):
    """Set all negative voluntary activations to zero"""
    print ('VA<0, times\n', df[['va', 'time'] ].loc[df['va'] < 0]) # list negative activations
    print('VA was not set at 0 for any baseline value, '
          '\nso there is no division-by-zero error for threshold')
    df['va'] = df['va'].clip(lower=0)
    return df

def _set_va_over_100_to_100(df: pd.DataFrame):
    """Set all voluntary activation values above 100% to 100%"""
    print('VA>100, times\n', df[['va', 'time'] ].loc[df['va'] > 100]) # list activations > 100%
    df['va'] = df['va'].clip(upper=100)
    return df

def _normalise(df: pd.DataFrame, varname: str):
    """For torque and resting twitch, normalise repeated measures values to baseline"""
    baseline = df[varname].values[0]
    normalised = df[varname].values / baseline * 100
    return normalised

def _difference(df: pd.DataFrame, varname: str):
    """For voluntary activation, take the difference of repeated measures values from baseline.
    Negative values indicate values are lower than baseline"""
    baseline = df[varname].values[0]
    difference = df[varname].values - baseline
    return difference

def _normalise_to_baseline(df: pd.DataFrame, id_list: list, varname: str):
    """Normalise repeated measures values to baseline or take the difference, and add to df"""
    normalised = []

    # hard code to normalise to baseline, sorted by session, ID
    for id in id_list:
        for sessionNum, session in zip([0, 1], ['pre', 'pos']):
            d_ = df.loc[df.id == id].loc[df.session == sessionNum]
            if varname == 'va':
                var = _difference(d_, varname)
            else:
                var = _normalise(d_, varname)
            normalised.append(var)

    normalised = np.array(normalised).flatten()
    df['n_' + varname] = normalised

    return df

def _predict(time, vals, order: int):
    """Fit polynomial to data, get predicted values"""
    # do polyfit on non-missing values only
    idx = np.isfinite(time) & np.isfinite(vals)
    if order == 1:
        coef = np.polyfit(time[idx], vals[idx], 1)
    elif order == 2:
        coef = np.polyfit(time[idx], vals[idx], 2)  # polyfit lists coefficients starting with highest order
    elif order == 3:
        coef = np.polyfit(time[idx], vals[idx], 3)
    elif order == 4:
        coef = np.polyfit(time[idx], vals[idx], 4)

    pred_time = np.arange(time[0], time[-1], 0.1)
    pred_vals = []
    for t in pred_time:
        if order == 1:
            v = (coef[0] * t) + coef[1]
        elif order == 2:
            v = (coef[0] * t ** 2) + (coef[1] * t) + coef[2]
        elif order == 3:
            v = (coef[0] * t ** 3) + (coef[1] * t ** 2) + (coef[2] * t) + coef[3]
        elif order == 4:
            v = (coef[0] * t ** 4) + (coef[1] * t ** 3) + (coef[2] * t ** 2) + (coef[3] * t) + coef[4]
        pred_vals.append(v)
    return pred_time, pred_vals

def _fit_data_by_id(df: pd.DataFrame, id_list: list, varname: str, path_proc: str, order=3, plot=True):
    """Fit outcome data over time, predict values, get time to recovery when outcome >= threshold of baseline"""
    n_varname = 'n_' + varname
    baseline_vals, fatigued_vals = [], []
    vals_at_15s = []
    recov_times, recov_vals = [], []

    # hard code to fit poly and predict values, sorted by session, ID
    for id in id_list:
        for sessionNum, session in zip([0, 1], ['pre', 'pos']):
            d_ = df.loc[df.id == id].loc[df.session == sessionNum]
            print('id:', id, ', sess:', session, ', var:', varname)
            # print(d_)

            # get non-normalised baseline values
            if d_[varname].values[0] is False:
                baseline_val = np.nan
            else:
                baseline_val = d_[varname].values[0]

            # calculate change in baseline to fatigued values, normalised to baseline
            if d_[n_varname].values[0] is False or d_[n_varname].values[1] is False:
                fatigued_val = np.nan
            else:
                fatigued_val = d_[n_varname].values[1] - d_[n_varname].values[0]

            # fit polynomial to varname and time, get predicted values
            if d_[n_varname][2:].isnull().all():
                # if baseline or time to recovery var are missing
                recov_val = np.nan
                recov_time = np.nan
            else:
                vals = d_[n_varname][2:].values
                time = d_.time[2:].values
                pred_time, pred_vals = _predict(time, vals, order=order)

                # get time when predicted value is at least 95% of baseline. Values are already normalised
                threshold = 95
                val_at_15s = pred_vals[0]
                for i, val in enumerate(pred_vals):
                    # fatigued VA is measured as fatigued - baseline difference
                    # define recovery as fatigued - baseline difference of at least 5%
                    if varname == 'va':
                        if val >= (100 - threshold) * -1:
                            recov_idx = i
                            break
                        else:
                            recov_idx = np.nan
                    # fatigued torque, resting twitch are measured as % of baseline
                    else:
                        if val >= threshold:
                            recov_idx = i
                            break
                        else:
                            recov_idx = np.nan

                if recov_idx >= 0:
                    recov_val = pred_vals[recov_idx]
                    recov_time = pred_time[recov_idx]
                else:
                    recov_val = np.nan
                    recov_time = np.nan

            # write values to df in long form
            col_len = len(d_[varname].values)
            baseline_vals_id = np.ones(col_len) * baseline_val
            baseline_vals.append(baseline_vals_id)

            fatigued_vals_id = np.ones(col_len) * fatigued_val
            fatigued_vals.append(fatigued_vals_id)

            vals_at_15s_id = np.ones(col_len) * val_at_15s
            vals_at_15s.append(vals_at_15s_id)

            recov_times_id = np.ones(col_len) * recov_time
            recov_times.append(recov_times_id)

            recov_vals_id = np.ones(col_len) * recov_val
            recov_vals.append(recov_vals_id)

            if plot:
                if np.isnan(d_[n_varname].values[0]) or np.isnan(d_[n_varname].values[1]):
                    pass

                else:
                    fig, ax = plt.subplots(figsize=(6, 3))
                    ax1 = plt.subplot(1, 4, 1)
                    ax1.plot(d_.time[0:2].values, d_[n_varname][0:2].values, 'k', alpha=0.5)
                    ax1.set_xticks([-30, 0])
                    ax1.set_xticklabels(['baseline', 'fatigued'])
                    ax1.spines['right'].set_visible(False)
                    ax1.spines['top'].set_visible(False)
                    if varname == 'va':
                        ax1.set_ylabel(varname + ' (%)')
                    else:
                        ax1.set_ylabel(varname + ' (%MVC)')

                    ax2 = plt.subplot(1, 4, (2,4))
                    ax2.plot(time, vals, 'ok', markersize=4, alpha=0.5)
                    ax2.plot(pred_time, pred_vals, 'k', alpha=0.5)
                    if recov_idx >= 0:
                        ax2.plot(recov_time, recov_val, 'or', markersize=4, label='recovered')
                    # plt.ylim(top=max(pred_vals) + 0.1*max(pred_vals))
                    plt.legend()
                    ax2.spines['right'].set_visible(False)
                    ax2.spines['top'].set_visible(False)
                    ax2.set_xlabel('time (s)')
                    if varname == 'va':
                        ax2.set_ylabel(varname + ' (%)')
                    else:
                        ax2.set_ylabel(varname + ' (%MVC)')

                    plt.tight_layout()
                    plt.savefig(path_proc / Path('sub' + str(id), 'recov_' + varname + '_' + session + '.png'), dpi=300)
                    plt.close()

    baseline_vals = np.array(baseline_vals).flatten()
    fatigued_vals = np.array(fatigued_vals).flatten()
    vals_at_15s = np.array(vals_at_15s).flatten()
    recov_times = np.array(recov_times).flatten()
    recov_vals = np.array(recov_vals).flatten()

    df['bv_' + varname] = baseline_vals
    df['fv_' + varname] = fatigued_vals
    df['ev_' + varname] = vals_at_15s
    df['rt_' + varname] = recov_times
    df['rv_' + varname] = recov_vals

    return df

def _plot_data_all(df: pd.DataFrame, id_list: list, varname: str, path_proc: str):
    """Sort by session: plot repeated measures data by id, group"""
    n_varname = 'n_' + varname
    for sessionNum, session in zip([0, 1], ['pre', 'pos']):
        df_sess = df[df.session == sessionNum]

        fig, ax = plt.subplots(figsize=(6, 3)) # OR fig = plt.figure(); ax1 = fig.add_suplot(1,1,1)
        ax1 = plt.subplot(1, 3, 1)
        ax2 = plt.subplot(1, 3, (2, 3))

        for id in id_list:
            # plot using unblinded group codes
            if df_sess[df_sess.id == id].group_unblind.iloc[0] == 0:
                if id == 34: # plot legend only once
                    ax1.plot(df_sess[df_sess.id == id].time[0:2].values,
                             df_sess[df_sess.id == id][n_varname][0:2].values, '0.5', alpha=0.5, label='con')
                    ax2.plot(df_sess[df_sess.id == id].time[3:].values,
                             df_sess[df_sess.id == id][n_varname][3:].values, '0.5', alpha=0.5, label='con')
                else:
                    ax1.plot(df_sess[df_sess.id == id].time[0:2].values,
                             df_sess[df_sess.id == id][n_varname][0:2].values, '0.5', alpha=0.5)
                    ax2.plot(df_sess[df_sess.id == id].time[3:].values,
                             df_sess[df_sess.id == id][n_varname][3:].values, '0.5', alpha=0.5)
            elif df_sess[df_sess.id == id].group_unblind.iloc[0] == 1:
                if id == 1:
                    ax1.plot(df_sess[df_sess.id == id].time[0:2].values,
                             df_sess[df_sess.id == id][n_varname][0:2].values, 'k', alpha=0.5, label='trt')
                    ax2.plot(df_sess[df_sess.id == id].time[3:].values,
                             df_sess[df_sess.id == id][n_varname][3:].values, 'k', alpha=0.5, label='trt')
                else:
                    ax1.plot(df_sess[df_sess.id == id].time[0:2].values,
                             df_sess[df_sess.id == id][n_varname][0:2].values, 'k', alpha=0.5)
                    ax2.plot(df_sess[df_sess.id == id].time[3:].values,
                             df_sess[df_sess.id == id][n_varname][3:].values, 'k', alpha=0.5)

        # pre-post fatigue
        ax1.set_xticks([-30, 0])
        ax1.set_xticklabels(['baseline', 'fatigued'])
        ax1.spines['right'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        if varname == 'va':
            ax1.set_ylabel(varname + ' (%)')
        else:
            ax1.set_ylabel(varname + ' (%MVC)')

        # recovery
        ax2.spines['right'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.set_xlabel('time (s)')
        if varname == 'va':
            ax2.set_ylabel(varname + ' (%)')
        else:
            ax2.set_ylabel(varname + ' (%MVC)')

        plt.legend()
        plt.tight_layout()
        plt.savefig(path_proc / Path('recov_' + varname + '_' + session + '.png'), dpi=300)
        plt.close()
