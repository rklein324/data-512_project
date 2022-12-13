# -*- coding: utf-8 -*-
'''
Created on Tue Nov  1 16:18:18 2022

@author: rebec
'''

###########
# IMPORTS #
###########

# import libraries
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

# read in data
mask_mandates = pd.read_csv("../filtered_raw_data/indiana_masks.csv")
cases = pd.read_csv('../filtered_raw_data/indiana_cases.csv')
vaccination = pd.read_csv('../filtered_raw_data/indiana_vaccination.csv')
svi = pd.read_csv('../filtered_raw_data/indiana_svi.csv')

#########################
# ANALYZE MASK MANDATES #
#########################

# clean mask mandate data
indiana_mask_mandates = mask_mandates[mask_mandates["FIPS_State"] == 18]
indiana_mask_mandates.dropna(subset=['Face_Masks_Required_in_Public'], inplace=True)
indiana_mask_mandates['date'] = pd.to_datetime(indiana_mask_mandates['date'])
indiana_mask_mandates.drop(columns=['County_Name'], inplace=True)

# compare mask mandates by county
sample_county = indiana_mask_mandates[indiana_mask_mandates["FIPS_County"] == 1].sort_values('date').drop(columns=['FIPS_County']).reset_index(drop=True)
compare_mandates = indiana_mask_mandates.groupby('FIPS_County').apply(lambda x: sample_county.equals(x.drop(columns=['FIPS_County']).sort_values('date').reset_index(drop=True)))
diff_mandates = compare_mandates[compare_mandates==False]
# this is an empty series, meaning all counties had the exact same mandates

###############
# ANALYZE SVI #
###############

# clean and pivot cases data
cases.dropna(subset=['FIPS'], inplace=True)
cases = cases.loc[(cases["Province_State"] == "Indiana") & (~cases["Admin2"].isin(["Unassigned", 'Out of IN']))]
cases['FIPS'] = cases['FIPS'].astype(int)
cases_pvt = cases[cases.columns[np.r_[6, 11:cases.shape[1]-1]]].set_index('FIPS')
cases_pvt = cases_pvt.melt(ignore_index=False).reset_index()
cases_pvt.columns = ['FIPS', 'Date', 'cases']
cases_pvt['Date'] = pd.to_datetime(cases_pvt['Date'])

# filter dates
cases_filt = cases_pvt.loc[(cases_pvt['Date'] >= '2021-01-01')]

# clean vaccination data
vaccination.dropna(subset=['FIPS'], inplace=True)
vaccination_filt = vaccination[vaccination['FIPS'].str.isnumeric()==True]
vaccination_filt['FIPS'] = vaccination_filt['FIPS'].astype(int)
vaccination_filt = vaccination_filt[['FIPS', 'Date', 'Series_Complete_Pop_Pct', 'Series_Complete_12PlusPop_Pct',
                                     'Series_Complete_18PlusPop_Pct', 'Series_Complete_65PlusPop_Pct',
                                     'Census2019', 'Census2019_12PlusPop', 'Census2019_18PlusPop']]
vaccination_filt['Date'] = pd.to_datetime(vaccination_filt['Date'])

# join cases and vaccination data
cases_vaccination = pd.merge(cases_filt, vaccination_filt, how='left')

# normalize cases by population
cases_vaccination['cases_norm'] = cases_vaccination['cases']/cases_vaccination['Census2019']
cases_vaccination['cases_norm_12plus'] = cases_vaccination['cases']/cases_vaccination['Census2019_12PlusPop']
cases_vaccination['cases_norm_18plus'] = cases_vaccination['cases']/cases_vaccination['Census2019_18PlusPop']

# get cases rate
rate = cases_vaccination.groupby('FIPS').apply(lambda x: pd.Series(np.gradient(x["cases"]), x["Date"])).melt(value_name='cases_rate', ignore_index=False).reset_index()
cases_vaccination = pd.merge(cases_vaccination, rate, how='left')

# group counties as vulnerable if in top 10%
svi_filt = svi[['FIPS', 'RPL_THEMES', 'RPL_THEME1', 'RPL_THEME2', 'RPL_THEME3', 'RPL_THEME4']]
svi_filt['vulnerable'] = svi_filt['RPL_THEMES'] > .9
svi_filt['vulnerable1'] = svi_filt['RPL_THEME1'] > .9
svi_filt['vulnerable2'] = svi_filt['RPL_THEME2'] > .9
svi_filt['vulnerable3'] = svi_filt['RPL_THEME3'] > .9
svi_filt['vulnerable4'] = svi_filt['RPL_THEME4'] > .9

# join cases_vaccination with svi data
case_vac_svi = pd.merge(cases_vaccination, svi_filt, how='left')

# create variable lists for cummulative variables
comp_vars = ['cases_norm', 'cases_norm_12plus', 'cases_norm_18plus', 'Series_Complete_Pop_Pct',
             'Series_Complete_12PlusPop_Pct', 'Series_Complete_18PlusPop_Pct', 'Series_Complete_65PlusPop_Pct']
date_vars = ['2021-01-01', '2021-04-01', '2021-07-01', '2021-10-01', '2022-01-01', '2022-04-01']
svi_vars = ['vulnerable', 'vulnerable1', 'vulnerable2','vulnerable3','vulnerable4']

# run t-tests on all combinations of cummulative variables
results = pd.DataFrame()
for date in date_vars:
    for svi in svi_vars:
        # define samples
        group1 = case_vac_svi.loc[(case_vac_svi['Date'] == date) & (case_vac_svi[svi] == True)]
        group2 = case_vac_svi.loc[(case_vac_svi['Date'] == date) & (case_vac_svi[svi] == False)]
        for comp in comp_vars:
            # perform Welch's t-test
            pvalue = ttest_ind(group1[comp], group2[comp], equal_var=False).pvalue
            # get group means
            vulnerable_mean = group1[comp].mean()
            not_vulnerable_mean = group2[comp].mean()
            # compare means
            mean_diff = vulnerable_mean - not_vulnerable_mean
            if comp in['cases_norm', 'cases_norm_12plus', 'cases_norm_18plus']:
                diff_status = 'better' if mean_diff<0 else 'worse'
            else:
                diff_status = 'better' if mean_diff>0 else 'worse'
            # save results to dataframe
            results = results.append(pd.DataFrame({'date': [date], 'var': [comp], 'svi_theme': [svi],
                                                   'pvalue': [pvalue], 'vulnerable_mean': [vulnerable_mean],
                                                   'not_vulnerable_mean': [not_vulnerable_mean],
                                                   'vulnerable_status': [diff_status]}))

# create variable lists for non-cummulative variables
comp_vars = ['cases_rate']
date_end_vars = ['2021-04-01', '2021-07-01', '2021-10-01', '2022-01-01', '2022-04-01']
svi_vars = ['vulnerable', 'vulnerable1', 'vulnerable2','vulnerable3','vulnerable4']

# run t-tests on all combinations of non-cummulative variables
date1 = '2021-01-01'
for date2 in date_end_vars:
    for svi in svi_vars:
        # define samples
        group1 = case_vac_svi.loc[(case_vac_svi['Date'] >= date1) & (case_vac_svi['Date'] < date2) & (case_vac_svi[svi] == True)]
        group2 = case_vac_svi.loc[(case_vac_svi['Date'] >= date1) & (case_vac_svi['Date'] < date2) & (case_vac_svi[svi] == False)]     
        for comp in comp_vars:
            # perform Welch's t-test
            pvalue = ttest_ind(group1[comp], group2[comp], equal_var=False).pvalue
            # get group means
            vulnerable_mean = group1[comp].mean()
            not_vulnerable_mean = group2[comp].mean()
            # compare means
            mean_diff = vulnerable_mean - not_vulnerable_mean
            diff_status = 'better' if mean_diff<0 else 'worse'
            # save results to dataframe
            results = results.append(pd.DataFrame({'date': [date1], 'var': [comp], 'svi_theme': [svi],
                                                   'pvalue': [pvalue], 'vulnerable_mean': [vulnerable_mean],
                                                   'not_vulnerable_mean': [not_vulnerable_mean],
                                                   'vulnerable_status': [diff_status]}))   
    # update begining of date range
    date1 = date2

# filter to significant results and sort
sig_results = results.loc[results['pvalue'] < .05]
sig_results.sort_values(['svi_theme', 'var', 'date'], inplace=True)

# rename theme variables
theme_names = {'vulnerable': 'Overall', 'vulnerable1': 'Socioeconomic Status',
               'vulnerable2': 'Household Characteristics', 'vulnerable3': 'Racial & Ethnic Minority Status',
               'vulnerable4': 'Housing Type & Transportation'}
sig_results=sig_results.replace({"svi_theme": theme_names})

# save results to csv
sig_results.to_csv('..//results//significant_results.csv', index=False)
