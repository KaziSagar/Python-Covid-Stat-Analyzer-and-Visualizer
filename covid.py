#sample datasets
#https://covidbd.000webhostapp.com/AFGsample.json
#https://covidbd.000webhostapp.com/BGDsample.json
#https://covidbd.000webhostapp.com/LARGEsample.json
#main dataset
#https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.json

import urllib.request, urllib.parse, urllib.error
import ssl
import json
import sqlite3

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('database.sqlite')
cur = conn.cursor()

#open these 4 lines when Database needs to be deleted
#cur.execute('''DROP TABLE IF EXISTS CoronaUpdate ''')
#cur.execute('''DROP TABLE IF EXISTS Country ''')
#cur.execute('''DROP TABLE IF EXISTS Continent ''')
#cur.execute('''DROP TABLE IF EXISTS DaysPer10k ''')

cur.execute('''CREATE TABLE IF NOT EXISTS Covid_BD
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Date TEXT UNIQUE,Total_Cases REAL, New_Cases REAL,
    Total_Deaths REAL, New_Deaths REAL, D_Case_Incrs,
    D_Death_Incrs, Daily_DR, O_Death_Rate REAL)''')

cur.execute('''CREATE TABLE IF NOT EXISTS DaysPer10k
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Days INTEGER)''')

url = input('\nEnter Dataset URL: ')
print('\nParsing data...')
print('Please wait! It may take long...')
data = urllib.request.urlopen(url, context=ctx).read()
print('\nData successfully parsed!')
info = json.loads(data)
print('\nUpdating database...')

count = 0
caseCount = 10000
per10k = 0
prvDay_Cases = 0
prvDay_Deaths = 0

daysPer10k = list()

for item in info["BGD"]:
    total_cases = 0.0
    new_cases = 0.0
    total_deaths = 0.0
    new_deaths = 0.0
    death_rate = 0.0
    daily_dr = 0.0

    try:
        date = item["date"]
        total_cases = float(item["total_cases"])
        new_cases = float(item["new_cases"])
        total_deaths = float(item["total_deaths"])
        new_deaths = float(item["new_deaths"])
        daily_dr = (100 * new_deaths)/new_cases
        death_rate = (100 * total_deaths)/total_cases
    except:
        pass

    case_increased = new_cases - prvDay_Cases
    death_increased = new_deaths - prvDay_Deaths

    cur.execute('INSERT OR IGNORE INTO Covid_BD (date, Total_Cases, New_Cases, Total_Deaths, New_Deaths, D_Case_Incrs, D_Death_Incrs, Daily_DR ,O_Death_Rate) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? )', ( date, total_cases, new_cases, total_deaths, new_deaths, case_increased, death_increased, daily_dr , death_rate, ) )

    prvDay_Cases = new_cases
    prvDay_Deaths = new_deaths

    count = count + 1
    if count % 30 == 1:
        conn.commit()

    per10k = per10k + 1
    if(total_cases>caseCount):
        caseCount = caseCount + 10000
        daysPer10k.append(per10k)
        per10k = 0
conn.commit()

for item in daysPer10k:
    cur.execute('INSERT OR IGNORE INTO DaysPer10k (Days) VALUES ( ? )', ( item, ) )
conn.commit()

print('\nDatabase successfully updated!')
print('\nExecute analyze.py to view analysis.')

cur.close()
