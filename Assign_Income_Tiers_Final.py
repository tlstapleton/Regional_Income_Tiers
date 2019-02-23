#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np


#Input the Regional Price Parities from the Bureau of Economic Analysis and the HH File summary output by Alteryx

price_parity=pd.read_csv('Inputs/Regional_Price_Parity.csv',header=4)
HHFile_Counts_By_CBSAMET=pd.read_csv('Inputs/HHFile_Counts_By_CBSAMET.csv')

#Adjust the U.S. Median HH Income if necessary (currently in 2016 dollars according to Pew Research Center)

median_us_income=67800


price_parity.drop(index=[0,385,386,387,388,389],inplace=True)
price_parity=price_parity[price_parity['2016']!='(NA)']


#Create function to round the income range numbers to the income breaks in the HH file

def income_round(x):
    min=50000
    rounded=250000
    for i in [0,15000,25000,35000,50000,75000,100000,125000,150000,175000,200000,250000]:
        if abs(x-i)<min:
            min=abs(x-i)
            rounded=i
    return rounded
        

income_ranges=pd.DataFrame(columns=['GeoFips','GeoName','2016'])

x=np.arange(1,6)
for i in x:
    price_parity['HH_Size']=np.repeat(i,len(price_parity))
    income_ranges=income_ranges.append(price_parity,sort=True)


income_ranges['2016']=income_ranges['2016'].astype(float)/100
income_ranges.reset_index().drop(columns='index')


#Calculate the middle income tier range for every HH size and CBSA Metro Area combination in the HH file

x=[]
y=[]
for i in np.arange(len(income_ranges)):
    x.append(((median_us_income)*(2/3)*(income_ranges.iloc[i]['HH_Size']**0.5)*income_ranges.iloc[i]['2016'])/(3**0.5))
    y.append(((median_us_income)*(2)*(income_ranges.iloc[i]['HH_Size']**0.5)*income_ranges.iloc[i]['2016'])/(3**0.5))
    
income_ranges['adjusted_low_threshold']=x
income_ranges['adjusted_high_threshold']=y


#Round the income ranges to match the breaks in the HH file

l=[]
h=[]
for i in np.arange(len(income_ranges)):
    l.append(income_round(income_ranges.iloc[i]['adjusted_low_threshold']))
    h.append(income_round(income_ranges.iloc[i]['adjusted_high_threshold']))
    
income_ranges['rounded_low_threshold']=l
income_ranges['rounded_high_threshold']=h

income_ranges.rename(columns={'GeoFips':'CBSAMET_KEY','HH_Size':'HH_SIZE'},inplace=True)
income_ranges['CBSAMET_KEY']=pd.to_numeric(income_ranges['CBSAMET_KEY'])


HHFile_Counts_By_CBSAMET['INCOME_NEW']=HHFile_Counts_By_CBSAMET['INCOME'].astype(str)
HHFile_Counts_By_CBSAMET[['HH_SIZE','other1','other2']]=HHFile_Counts_By_CBSAMET['SIZE1'].str.split(' ',expand=True)
HHFile_Counts_By_CBSAMET=HHFile_Counts_By_CBSAMET[['CBSAMET_KEY','CBSAMET_NAME','INCOME','INCOME_NEW','HH_SIZE','SIZE1','Count']]
HHFile_Counts_By_CBSAMET['HH_SIZE']=HHFile_Counts_By_CBSAMET['HH_SIZE'].str.extract('(\d+)')
HHFile_Counts_By_CBSAMET['HH_SIZE']=pd.to_numeric(HHFile_Counts_By_CBSAMET['HH_SIZE'])
HHFile_Counts_By_CBSAMET.head()


income_ranges.rename(columns={'GeoFips':'CBSAMET_KEY','HH_Size':'HH_SIZE'},inplace=True)

df=pd.merge(HHFile_Counts_By_CBSAMET,income_ranges,on=['CBSAMET_KEY','HH_SIZE'])


x=[]
for i in df['INCOME_NEW']:
        x.append(i.replace(',',''))
df['INCOME_NEW']=x

df[['low income','high income']]=df['INCOME_NEW'].str.split('-',expand=True)

df['low income']=df['low income'].str.extract('(\d+)')
df['high income']=df['high income'].str.extract('(\d+)')

for i in np.arange(len(df)):
    if (df['low income'][i]=='15000') & (df['high income'][i]!='24999'):
        df['low income'][i]=0
        df['high income'][i]=1500
    elif df['low income'][i]=='250000':
        df['high income'][i]=1000000


#Assign Income Tier

df['Income_Class']=''
for i in np.arange(len(df)):
    if (df['INCOME_NEW'][i]=='Unknown Income'):
        df['Income_Class'][i]='None'
    elif (int(df['low income'][i])>=int(df['rounded_low_threshold'][i])) & (int(df['high income'][i])<int(df['rounded_high_threshold'][i])):
        df['Income_Class'][i]='Middle'
    elif int(df['high income'][i])<=int(df['rounded_low_threshold'][i]):
        df['Income_Class'][i]='Lower'
    elif int(df['low income'][i])>=int(df['rounded_high_threshold'][i]):
        df['Income_Class'][i]='Upper'



df_IncomeTiers=df[['CBSAMET_KEY','CBSAMET_NAME','INCOME','SIZE1','Count','Income_Class']]

df_IncomeTiers.to_csv('income_tier_lookup_table.csv')

