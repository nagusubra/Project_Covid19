from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import seaborn as sns

# Read measurements from database, sqlalchemy URI
#Database is expected to have:
# - one table 'alberta' with:
#   - one column 'date' (an iso formated date string)
#   - one column 'daily_cases' (an int)
db_uri = 'sqlite:///../data/measurements.db'

engine = create_engine(db_uri, echo=False)
df = pd.read_sql_table(table_name='alberta', con=engine)
engine.dispose()

#Make sure dates are sorted
df = df.sort_values(by=['date'])

#Compute total and smoothed daily cases
df['total_cases'] = df.daily_cases.cumsum()
df['smooth_daily_cases'] = df.daily_cases.rolling(3).mean()

#Checking what we have
df.info()
print(df.head())

#Figure1: Seaborn plots for daily cases and total cases
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)

sns.barplot(x='date', y='daily_cases', data=df, ax=ax1,
            palette=sns.color_palette("Set2", 2))
sns.lineplot(x='date', y='total_cases', data=df, ax=ax2)

ax1.grid(b=True)
ax2.grid(b=True)
plt.xticks(rotation=45, horizontalalignment='right')
plt.tight_layout()

#Figure2: Matplotlib log-log plot of:
# - total_cases (x-axis) and 
# - smoothed daily_cases (y-axis)
# as used in: https://www.youtube.com/watch?v=54XLXg4fYsc
plt.figure()
x_str='total_cases'
y_str='smooth_daily_cases'
# using log-log and two minor ticks per decade
plt.loglog(df[x_str], df[y_str], subsx=[2, 5], subsy=[2, 5])
# Add a 'dot' to indicate last measurement
plt.plot(df[x_str].iloc[-1], df[y_str].iloc[-1], 'ko')
# labels
plt.xlabel(x_str)
plt.ylabel(y_str)
# grid on both major and minor ticks
plt.grid(which='both')
# formatting major and minor tick labels
ax = plt.gca()
ax.xaxis.set_major_formatter(FormatStrFormatter("%.0f"))
ax.xaxis.set_minor_formatter(FormatStrFormatter("%.0f"))
ax.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
ax.yaxis.set_minor_formatter(FormatStrFormatter("%.0f"))

# show both figures
plt.show()
