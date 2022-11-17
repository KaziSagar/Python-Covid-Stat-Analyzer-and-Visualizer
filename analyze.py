import sqlite3
import time
import zlib
import re

conn = sqlite3.connect('database.sqlite')
cur = conn.cursor()

cur.execute('''DROP TABLE IF EXISTS Monthly_Increase ''')

cur.execute('''CREATE TABLE IF NOT EXISTS Monthly_Increase
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Date TEXT UNIQUE, Cases REAL, Deaths REAL)''')

cur.execute('SELECT Date FROM Covid_BD')

main_list = list()
date_list = list()
case_list = list()
death_list = list()
caseIncrease_list = list()
deathIncrease_list = list()

cur.execute('SELECT Date, Total_Cases, Total_Deaths FROM Covid_BD')

prvCase = 0
prvDeath = 0

for date, case, death in cur:
    month = re.findall('([0-9]+-[0-9]+)-[0-9]+',date)
    month = month[0]

    if month not in date_list:
        date_list.append(month)

    caseEdge = case
    deathEdge = death
    #below if-statement is valid untill Year 2031
    if date.endswith('01-31') or date.endswith('02-28') or date.startswith('2024-02-29') or date.startswith('2028-02-29') or date.endswith('03-31') or date.endswith('04-30') or date.endswith('05-31') or date.endswith('06-30') or date.endswith('07-31') or date.endswith('08-31') or date.endswith('09-30') or date.endswith('10-31') or date.endswith('11-30') or date.endswith('12-31'):

        case_list.append(case)
        death_list.append(death)

        total_case_increase = case - prvCase
        caseIncrease_list.append(total_case_increase)
        prvCase = total_case_increase

        total_death_increase = death - prvDeath
        deathIncrease_list.append(total_death_increase)
        prvDeath = total_death_increase


caseEdge = caseEdge
deathEdge = deathEdge
increased_caseEdge = caseEdge - prvCase
increased_deathEdge = deathEdge - prvDeath

case_list.append(caseEdge)
death_list.append(deathEdge)
caseIncrease_list.append(increased_caseEdge)
deathIncrease_list.append(increased_deathEdge)
main_list.append(date_list)
main_list.append(case_list)
main_list.append(death_list)


counter = 0
for idx in range(len(date_list)+1):
    idxlen = len(date_list)
    if counter < idxlen:
        x = date_list[counter]
        y = caseIncrease_list[counter]
        z = deathIncrease_list[counter]
        cur.execute('INSERT OR IGNORE INTO Monthly_Increase (Date, Cases, Deaths) VALUES ( ?, ?, ? )', ( x, y, z, ) )
        counter = counter + 1
conn.commit()

#Displaying analysis
print('\n***** Bangladesh: Latest COVID-19 update *****\n')

cur.execute('SELECT Date, Total_Cases, New_cases, Total_Deaths, New_Deaths, D_Case_Incrs, D_Death_Incrs, Daily_DR, O_Death_Rate FROM Covid_BD ORDER BY ID DESC LIMIT 1')
for Date, Total_Cases, New_cases, Total_Deaths, New_Deaths, D_Case_Incrs, D_Death_Incrs, Daily_DR, O_Death_Rate in cur:
    print('Date:',Date)
    print('New cases:',New_cases)
    print('New deaths:',New_Deaths)
    print('Cases increased/decreased:',D_Case_Incrs)
    print('Deaths increased/decreased:',D_Death_Incrs)
    print('Today\'s death rate:',Daily_DR)
    print('Total cases:',Total_Cases)
    print('Total deaths:',Total_Deaths)
    print('Overall death rate:',O_Death_Rate)

print("\nLargest numbers seen in a single day:\n")
cur.execute('SELECT max(New_cases), max(New_Deaths), max(Daily_DR) FROM Covid_BD')
for New_cases, New_Deaths, Daily_DR in cur:
    print('Cases:',New_cases)
    print('Deaths:',New_Deaths)
    print('Death rate:',Daily_DR)

print("\nMonthly increase:\n")
cur.execute('SELECT Date, Cases, Deaths FROM Monthly_Increase')
for Date, Cases, Deaths in cur:
    print('Month:',Date,' ','Cases:',Cases,' ','Deaths:',Deaths)

print('\nEvery next 10k COVID-19 cases increased in:\n')
cur.execute('SELECT id, Days FROM DaysPer10k')
for id, Days in cur:
    print(id,'in',Days,'days')


fhand = open('gline.js','w')
fhand.write("gline = [ ['Month','Total Cases','Total Deaths']")

count = 0
for i in range((len(main_list))+1):
    ilen = len(date_list)
    if count < ilen:
        fhand.write(",\n['")
        c = 0
        for idx in main_list:
            strng = str(idx[count])
            if re.search('^[0-9]+-[0-9]+',strng):
                fhand.write(strng+"'")
                c = c+1
            elif c != (len(case_list))-1:
                fhand.write(', '+strng)
                c = c+1
        count = count + 1
        fhand.write("]")
fhand.write("\n];")

fhand.close()
cur.close()

print("\n\nOutput written to gline.js")
print("Open gline.htm to visualize the data")
