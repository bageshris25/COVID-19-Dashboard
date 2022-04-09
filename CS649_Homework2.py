#!/usr/bin/env python
# coding: utf-8

# In[32]:


from re import X
import json
import pandas as pd
import streamlit as st
import datetime as dt
from urllib.request import urlopen
import plotly.express as px


base_path = "./"
confirmed_cases = (base_path+'covid_confirmed_usafacts.csv')
covid_deaths = (base_path+'covid_deaths_usafacts.csv')
county_population = (base_path+'covid_county_population_usafacts.csv')


confirmed_cases_df = pd.read_csv(confirmed_cases)
death_cases_df = pd.read_csv(covid_deaths)
county_population_df = pd.read_csv(county_population)
st.title('Analysis Dashboard of Covid-19')


#Question 1

def new_cases_weekly_data():
    all_cols = list(confirmed_cases_df.columns)
    cols = ['countyFIPS','County Name','State','StateFIPS']
    for col in cols:
        all_cols.remove(col)
    new_cases_weekly_df = pd.melt(confirmed_cases_df, id_vars = confirmed_cases_df.loc[:,cols], value_vars = confirmed_cases_df.loc[:,all_cols],
                    var_name = 'Date',value_name = 'Confirmed Cases of Covid-19')
    new_cases_weekly_df['Date'] = pd.to_datetime(new_cases_weekly_df['Date'])
    new_cases_weekly_df = new_cases_weekly_df.groupby(['Date']).sum().reset_index()
    new_cases_weekly_df = new_cases_weekly_df.loc[new_cases_weekly_df['countyFIPS'] != 0]
    new_cases_weekly_df['Confirmed Cases of Covid-19'] = new_cases_weekly_df['Confirmed Cases of Covid-19'].diff()
    new_cases_weekly_df = new_cases_weekly_df.groupby( pd.Grouper(key='Date', freq='W-SAT'))[['Date','Confirmed Cases of Covid-19']].filter(lambda x: len(x) == 7)
    new_cases_weekly_df = new_cases_weekly_df.groupby( pd.Grouper(key='Date', freq='W-SAT'))['Confirmed Cases of Covid-19'].sum().to_frame()
    return new_cases_weekly_df

weekly_confirmed_new_cases = new_cases_weekly_data()
st.write("New Cases of Covid-19 per week")
st.line_chart(weekly_confirmed_new_cases['Confirmed Cases of Covid-19'])


#Question 2

def weekly_deaths_data():
    all_cols = list(death_cases_df.columns)
    cols = ['countyFIPS','County Name','State','StateFIPS']
    for col in cols:
        all_cols.remove(col)
    death_cases_weekly_df = pd.melt(death_cases_df, id_vars=death_cases_df.loc[:,cols], value_vars = death_cases_df.loc[:,all_cols],
                    var_name = 'Date',value_name = 'Death Count of Covid -19')
    death_cases_weekly_df['Date'] = pd.to_datetime(death_cases_weekly_df['Date'])
    death_cases_weekly_df = death_cases_weekly_df.groupby(['Date'])['Death Count of Covid -19'].sum().reset_index()
    death_cases_weekly_df['Death Count of Covid -19'] = death_cases_weekly_df['Death Count of Covid -19'].diff()
    death_cases_weekly_df = death_cases_weekly_df.groupby( pd.Grouper(key='Date', freq='W-SAT'))[['Date','Death Count of Covid -19']].filter(lambda x: len(x) == 7)
    death_cases_weekly_df = death_cases_weekly_df.groupby( pd.Grouper(key='Date', freq='W-SAT'))['Death Count of Covid -19'].sum().to_frame()

    return death_cases_weekly_df

weekly_confirmed_death_cases = weekly_deaths_data()
st.write("Death Cases of Covid-19 per week")
st.line_chart(weekly_confirmed_death_cases['Death Count of Covid -19'])




allcount_of_cases = confirmed_cases_df.drop(['County Name'],axis = 1)

combined_count = confirmed_cases_df.groupby(['countyFIPS']).sum().diff(axis=1)
cols = list(combined_count.columns)
cols.remove('StateFIPS')
temp_df = pd.DataFrame(cols,columns = ['Date'])
temp_df['Date'] = pd.to_datetime(temp_df['Date'])
temp_df = temp_df.groupby( pd.Grouper(key='Date', freq='W-SAT'))[['Date']].filter(lambda x: len(x) == 7)
temp_df['Date'] = temp_df.Date.dt.strftime('%Y-%m-%d')

combined_count = combined_count.loc[:,temp_df.Date.values]
low_end = temp_df.Date.values[0]
higher_end = temp_df.Date.values[len(temp_df.Date.values)-1]


total_no_rows = (combined_count.shape[1])
combined_count = combined_count.groupby([[i//7 for i in range(0, total_no_rows)]], axis = 1).sum().T

date_value = pd.period_range(start = low_end , end = higher_end, freq = 'W-SAT')
date_value = date_value.map(str)
date_value = date_value.str.split('/').str[0]
date_value = pd.Series(date_value)

combined_count = combined_count.assign(Weeks = date_value)
combined_count = combined_count.set_index(['Weeks'])
combined_count= combined_count.T

covid_county_population = pd.read_csv(county_population)
covid_county_population = covid_county_population.groupby('countyFIPS').sum()

combined_count.merge(covid_county_population, how = 'outer', on = 'countyFIPS')
county_add = combined_count.iloc[::, :].mul(100000, axis = 1).div(covid_county_population['population'],axis = 0)
combined_count.dropna(inplace= True)
combined_count.reset_index(level= 0 , inplace= True)
combined_count ['countyFIPS'] = combined_count['countyFIPS'].astype(str).str.zfill(5)
#combined_count




# In[9]:


allcount_of_deaths = death_cases_df.drop(['County Name'],axis = 1)

combined_death_count = death_cases_df.groupby(['countyFIPS']).sum().diff(axis=1)

cols = list(combined_death_count.columns)
cols.remove('StateFIPS')
temp_df = pd.DataFrame(cols,columns = ['Date'])
temp_df['Date'] = pd.to_datetime(temp_df['Date'])
temp_df = temp_df.groupby( pd.Grouper(key='Date', freq='W-SAT'))[['Date']].filter(lambda x: len(x) == 7)
temp_df['Date'] = temp_df.Date.dt.strftime('%Y-%m-%d')

combined_death_count = combined_death_count.loc[:,temp_df.Date.values]
low_end = temp_df.Date.values[0]
higher_end = temp_df.Date.values[len(temp_df.Date.values)-1]


total_no_rows = (combined_death_count.shape[1])
combined_death_count = combined_death_count.groupby([[i//7 for i in range(0, total_no_rows)]], axis = 1).sum().T

date_value = pd.period_range(start = low_end , end = higher_end, freq = 'W-SAT')
date_value = date_value.map(str)
date_value = date_value.str.split('/').str[0]
date_value = pd.Series(date_value)

combined_death_count = combined_death_count.assign(Weeks = date_value)
combined_death_count = combined_death_count.set_index(['Weeks'])
combined_death_count= combined_death_count.T

covid_county_population = pd.read_csv(county_population)
covid_county_population = covid_county_population.groupby('countyFIPS').sum()

combined_death_count.merge(covid_county_population, how = 'outer', on = 'countyFIPS')
county_add = combined_death_count.iloc[::, :].mul(100000, axis = 1).div(covid_county_population['population'],axis = 0)
combined_death_count.dropna(inplace= True)
combined_death_count.reset_index(level= 0 , inplace= True)
combined_death_count ['countyFIPS'] = combined_death_count['countyFIPS'].astype(str).str.zfill(5)



columns_list = combined_count.iloc[::, 1:].columns.to_list()
option = st.select_slider(
'Choose the start of the week',
options=columns_list
)

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    county = json.load(response)
    
st.write("Question 3 solution")
fig1 = px.choropleth(combined_count,
                        geojson = county,
                        locations='countyFIPS',
                        color = option,
                        color_continuous_scale='earth',
                        scope="usa",
                        labels={'County Cases': 'Cases per 100,000'},)
fig1

st.write("Question 4 and Question 5 solution")
fig2 = px.choropleth(combined_death_count,
                     geojson=county,
                     locations='countyFIPS',
                     color = option,
                     color_continuous_scale='sunset',
                     range_color=(0, 20),
                     scope="usa",
                     labels={'County Cases': 'Cases per 100,000'},
                     )
fig2


if st.button("Animation"):
    for date in combined_count.iloc[::, 1:].columns.to_list():
        fig1 = px.choropleth(combined_count,
                        geojson = county,
                        locations='countyFIPS',
                        color = option,
                        color_continuous_scale='earth',
                        scope="usa",
                        labels={'County Cases': 'Cases per 100,000'},)
        fig2 = px.choropleth(combined_death_count,
                     geojson=county,
                     locations='countyFIPS',
                     color = option,
                     color_continuous_scale='sunset',
                     range_color=(0, 20),
                     scope="usa",
                     labels={'County Cases': 'Cases per 100,000'},
                     )


# In[ ]:




