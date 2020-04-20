import sqlite3
import argparse
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-a','--add', 
                    help='Add number of measurements today, or on date selected by -d')
parser.add_argument('-d', '--date', 
                    help='Choose a date with YYYY-MM-DD format')
parser.add_argument('-r', '--remove', action='store_true', 
                    help='Remove measurement today, or on date selected by -d')
parser.add_argument('-l', '--list', action='store_true', 
                    help='List all database entries')
args = parser.parse_args()

#Connect to hard coded database
#Database is expected to have:
# - one table 'alberta' with:
#   - one column 'date' (an iso formated date string)
#   - one column 'daily_cases' (an int)
# values until 2020-03-29 from case counts https://covid19stats.alberta.ca
db_str = '../data/measurements.db'
#db_str = 'C:\DIGIENGG\LAB\a6-web-data-to-graph-nagusubra\data\measurements.db'
conn = sqlite3.connect(db_str)
c = conn.cursor()

print('Connection to {} open'.format(db_str))


if args.list:
    #Using select and fetchall to get all db entries.
    c.execute('select * from alberta')
    for item in c.fetchall():
        print(item)
else:
    
    # If no date was supplied, we use today
    if args.date is not None:
        t = (args.date, )
    else:
        t = (datetime.date.today().isoformat(), )
    
    # There should either be one entry or none at any given date
    c.execute('select daily_cases from alberta where date=?', t)
    measurement = c.fetchone()
    
    # fetchnone() returns None if no entries were found.
    if measurement is not None:
        print('We have {} measurements for {}'.format(measurement[0], t[0]))
        # There is an entry, if the user asked to remove, confirm first.
        if args.remove is not None:
            ans = input('Remove? (y/n) :')
            if 'y' in ans.lower():
                c.execute('delete from alberta where date=?', t)
                conn.commit() #commit to have change take effect.
    else:
        print('We do NOT have measurements for {}'.format(t[0]))
        # There is no entry and the sure supplied a number to add.
        if args.add is not None:
            print('   Adding {}'.format(args.add))
            t = (t[0], args.add)
            c.execute('insert into alberta values (?, ?)', t)
            conn.commit() #commit to have change take effect.
    
conn.close()
