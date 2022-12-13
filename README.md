# The Social Vulnerability Index and the COVID-19 Pandemic
## Abstract
This analysis was performed for the final project in the DATA 512 (Human-Centered Data Science) class at the University of Washington as part of the Masters of Science in Data Science. It explores the relationship between socially vulnerable counties in Indiana and their respective number of covid cases and vaccination rate.

## Liscenses
CDC sourced data: [Data User Agreement](https://www.cdc.gov/nchs/data_access/restrictions.htm)  
Covid case data: [Liscence: Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

## Filtered Raw Data Files
In order to upload the data to github, the raw data was filtered to Indiana. The code to do the filtering is still included in the src file for ease of use if updated data is desired.

### Mask Mandates
**filename:** indiana_masks.csv  
**source:** [CDC](https://data.cdc.gov/Policy-Surveillance/U-S-State-and-Territorial-Public-Mask-Mandates-Fro/62d6-pm5i)

| Relevant Column | Description |
| ------- | ------------- |
| FIPS_State | U.S. state FIPS codes |
| FIPS_County | U.S. county FIPS codes |
| date | Daily date in dataset |
| Face_Masks_Required_in_Public | A requirement for individuals operating in a personal capacity to wear masks 1) anywhere outside their homes or 2) both in retail businesses and in restaurants/food establishments. |

### COVID Cases
**filename:** indiana_cases.csv  
**source:** [Johns Hopkins University](https://www.kaggle.com/datasets/antgoldbloom/covid19-data-from-john-hopkins-university)

| Relevant Column | Description |
| ------- | ------------- |
| FIPS | Federal Information Processing Standard State Code |
| *date* | each date has its own column containing the cumulative count of confirmed cases of COVID |

### Vaccination
**filename:** indiana_vaccination.csv  
**source:** [CDC](https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-County/8xkx-amqh)

| Relevant Column | Description |
| ------- | ------------- |
| Date | Date data are reported on CDC COVID Data Tracker |
| FIPS | Federal Information Processing Standard State Code |
| Series_Complete_Pop_Pct | Percent of people who have completed a primary series (have second dose of a two-dose vaccine or one dose of a single-dose vaccine) based on the jurisdiction and county where vaccine recipient lives |
| Series_Complete_12PlusPop_Pct | Percent of people ages 12+ who have completed a primary series (have second dose of a two-dose vaccine or one dose of a single-dose vaccine) based on the jurisdiction and county where vaccine recipient lives |
| Series_Complete_18PlusPop_Pct | Percent of people ages 18+ who have completed a primary series (have second dose of a two-dose vaccine or one dose of a single-dose vaccine) based on the jurisdiction and county where vaccine recipient lives |
| Series_Complete_65PlusPop_Pct | Percent of people ages 65+ who have completed a primary series (have second dose of a two-dose vaccine or one dose of a single-dose vaccine) based on the jurisdiction and county where vaccine recipient lives |
| Census2019 | 2019 Census Population |
| Census2019_12PlusPop | 2019 Census Population for ≥12 years of age |
| Census2019_18PlusPop | 2019 Census Population for ≥18 years of age |

### Social Vulnerability Index
**filename:** indiana_svi.csv  
**source:** [CDC](https://www.atsdr.cdc.gov/placeandhealth/svi/interactive_map.html)

| Relevant Column | Description |
| ------- | ------------- |
| FIPS | Tract-level FIPS code |
| RPL_THEMES | Overall percentile ranking |
| RPL_THEME1 | Percentile ranking for Socioeconomic Status theme summary |
| RPL_THEME2 | Percentile ranking for Household Characteristics theme summary |
| RPL_THEME3 | Percentile ranking for Racial and Ethnic Minority Status theme |
| RPL_THEME4 | Percentile ranking for Housing Type/ Transportation theme |

## Results Data File
**filename:** significant_results.csv  
Includes data for all t-tests that had a p-value <0.05.

| Relevant Column | Description |
| ------- | ------------- |
| date | date of cumulative variables or first date of 3-month range for the cases_rate variable |
| var | variable run through t-test (see table below) |
| svi_theme | Either 'Overall' or one of the SVI themes listed in the Social Vulnerability Index |
| pvalue | the pvalue of the t-test run using the mean of the var at the date (or through the date range) between vulnerable (top 10%) and non-vulnerable counties according to the svi_theme |
| vulnerable_mean | the mean used in the t-test for vulnerable counties |
| not_vulnerable_mean | the mean used in the t-test for non-vulnerable counties |
| vulnerable_status | 'better' if the vulnerable county mean is better than the non-vulnerable county mean, 'worse' otherwise |

| Variable | Description |
| ------- | ------------- |
| cases_rate | rate of cases using numpy's gradient on COVID Cases raw data |
| cases_norm | cumulative count of cases from COVID Cases raw data normalized by dividing by Census2019 variable from Vaccination raw data|
| cases_norm_12plus | cumulative count of cases from COVID Cases raw data normalized by dividing by Census2019_12PlusPop variable from Vaccination raw data |
| cases_norm_18plus | cumulative count of cases from COVID Cases raw data normalized by dividing by Census2019_18PlusPop variable from Vaccination raw data |
| Series_Complete_Pop_Pct | see Vaccination raw data description |
| Series_Complete_12PlusPop_Pct | see Vaccination raw data description |
| Series_Complete_18PlusPop_Pct | see Vaccination raw data description |
| Series_Complete_65PlusPop_Pct | see Vaccination raw data description |
