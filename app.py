import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}
gdp = pd.read_excel('data/gdplev.xls', skiprows = 7, usecols= {'Unnamed: 4', 'Unnamed: 6'})
gdp = gdp.loc[212:]
gdp = gdp.rename(columns = {'Unnamed: 4': 'Quarter', 'Unnamed: 6': 'GDP'})
gdp['GDP'] = pd.to_numeric(gdp['GDP'])



def get_recession_start():
    quarters = []
    for i in range(len(gdp) - 2):
        if (gdp.iloc[i][1] > gdp.iloc[i+1][1]) & (gdp.iloc[i+1][1] > gdp.iloc[i+2][1]):
            quarters.append(gdp.iloc[i+1][0])
    return quarters[0]




def get_recession_end():
    gdp2 = gdp.loc[245:]
    recession_end = []
    for i in range(len(gdp2)- 2):
        if (gdp2.iloc[i+2][1] > gdp2.iloc[i+1][1])  & (gdp2.iloc[i+1][1] > gdp2.iloc[i][1]):
            recession_end.append(gdp2.iloc[i+2][0])
    return recession_end[0]




def get_recession_bottom():
    recession_period = gdp.loc[245:]
    recession_min = recession_period[recession_period['GDP'] == recession_period['GDP'].min()]
    return recession_min.values[0][0]




def get_list_of_university_towns():
    with open('data/university_towns.txt') as file:
        data = []
        for line in file:
            data.append(line[:-1])
    state_town = []
    for line in data:
        if line[-6:] == '[edit]':
            state = line[:-6]
        elif '(' in line:
            town = line[:line.index('(')-1]
            state_town.append([state,town])
        else:
            town = line
            state_town.append([state,town])
    state_college_df = pd.DataFrame(state_town,columns = ['State','RegionName'])
    return state_college_df




def convert_housing_data_to_quarters():
    housingdata_df = pd.read_csv('data/City_Zhvi_AllHomes.csv')
    housingdata_df['State'] = housingdata_df['State'].map(states)
    housingdata_df.set_index(["State","RegionName"], inplace=True)
    housingdata_df = housingdata_df.filter(regex='^20', axis=1)
    housingdata_df = housingdata_df.groupby(pd.PeriodIndex(housingdata_df.columns, freq='Q'), axis=1).mean()
    return housingdata_df



recession_start = get_recession_start()
recession_bottom = get_recession_bottom()
university_towns = get_list_of_university_towns()

housingdata_df = convert_housing_data_to_quarters().dropna()
hdf = housingdata_df.copy()

ratio = pd.DataFrame({'ratio': hdf[recession_start].div(hdf[recession_bottom])})

hdf.columns = hdf.columns.to_series().astype(str)
hdf = pd.concat([hdf, ratio], axis=1)

hdf = pd.DataFrame(hdf)
hdf.reset_index(['State','RegionName'], inplace = True)

unitown_priceratio = hdf.loc[list(university_towns.index)]['ratio'].dropna()
nonunitown_priceratio_index = set(hdf.index) - set(unitown_priceratio)
nonunitown_priceratio = hdf.loc[list(nonunitown_priceratio_index),:]['ratio'].dropna()
def run_ttest(a, b):
    tstat, p = tuple(ttest_ind(a, b))
    
    different = p < 0.05
    result = tstat < 0
    better = ["university town", "non-university town"]
    
    return (different, p, better[result])
    
print(run_ttest(unitown_priceratio, nonunitown_priceratio))