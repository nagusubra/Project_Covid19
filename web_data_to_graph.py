# Author: Subramanian Narayanan
'''This Flask application is to take data from measurements.db which is updated using sqlite through python command interface
   The Flask application displays the table of data from the databas and also shows the 3 plots 
        Daily new infections as a function of time as a barplot.
        Total infections as a function of time as a lineplot.
        Total infections (x-axis) and daily new infections smoothed with moving average (y-axis) on a log-log plot.
   The Flask server uses index.html, plot.html and table.html along with style.css to display the content 
'''

from flask import Flask, render_template
import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import inspect
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import io

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

app = Flask(__name__)

db_uri = 'sqlite:///data/measurements.db'

@app.route('/')
def index():
    now = datetime.datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M")

    engine = create_engine(db_uri, echo=False)
    inspector = inspect(engine)
    df = inspector.get_table_names()
    engine.dispose()
    return render_template('index.html', time=time_string, datasets=df)

@app.route('/dataset/<name>')
def dataset(name):
    try:
        engine = create_engine(db_uri, echo=False)
        df = pd.read_sql_table(table_name=name, con=engine)
        engine.dispose()
        #Make sure dates are sorted
        df = df.sort_values(by=['date'])

        #Compute total and smoothed daily cases
        df['total_cases'] = df.daily_cases.cumsum()
        df['smooth_daily_cases'] = df.daily_cases.rolling(3).mean()
        
    except:
        return render_template('table.html', name=name, columns='', dataset='Values not found.')
    else:
        return render_template('table.html', name=name, columns=df.columns, dataset=df.to_html(index=False))

'''
Route to a plotting function in flask server. It is responsible for displaying the graph of Daily new infections as a function of time as a barplot.
This code is to produce Matplotlib figures in svg format embedded in response HTML.
'''

@app.route('/plot_graph1/<name>')
def plot_graph1(name):
    try:
        engine = create_engine(db_uri, echo=False)
        df = pd.read_sql_table(table_name='alberta', con=engine)
        engine.dispose()
        df['total_cases'] = df.daily_cases.cumsum()
        df['smooth_daily_cases'] = df.daily_cases.rolling(3).mean()

        fig = Figure()
        FigureCanvas(fig)

        fig, (ax) = plt.subplots(nrows=1, ncols=1, sharex=True)
        
        sns.barplot(x='date', y='daily_cases', data=df, ax=ax, palette=sns.color_palette("Set2", 2))
        ax.grid(b=True)
        plt.xticks(rotation=65, horizontalalignment='right')
        plt.tight_layout()

        img = io.StringIO()
        fig.savefig(img, format='svg')
        #clip off the xml headers from the image
        svg_img = '<svg' + img.getvalue().split('<svg')[1]

    except:
        return render_template('plot.html', name=name, txtx ='', plot='Values not found.')
    else:
        return render_template('plot.html', name=name, txtx ='Daily new infections as a function of time as a barplot', plot=svg_img)


'''
Route to a plotting function in flask server. It is responsible for displaying the graph of Total infections as a function of time as a lineplot.
This code is to produce Matplotlib figures in svg format embedded in response HTML.
'''

@app.route('/plot_graph2/<name>')
def plot_graph2(name):
    try:
        engine = create_engine(db_uri, echo=False)
        df = pd.read_sql_table(table_name='alberta', con=engine)
        engine.dispose()
        df = df.sort_values(by=['date'])
        df['total_cases'] = df.daily_cases.cumsum()
        df['smooth_daily_cases'] = df.daily_cases.rolling(3).mean()

        fig = Figure()
        FigureCanvas(fig)

        fig, (ax) = plt.subplots(nrows=1, ncols=1, sharex=True)
        
        sns.lineplot(x='date', y='total_cases', data=df, ax=ax)
        ax.grid(b=True)
        plt.xticks(rotation=65, horizontalalignment='right')
        plt.tight_layout()

        img = io.StringIO()
        fig.savefig(img, format='svg')
        #clip off the xml headers from the image
        svg_img = '<svg' + img.getvalue().split('<svg')[1]

    except:
        return render_template('plot.html', name=name, txtx ='',plot='Values not found.')
    else:
        return render_template('plot.html', name=name, txtx ='Total infections as a function of time as a lineplot',plot=svg_img)


'''
Route to a plotting function in flask server. It is responsible for displaying the graph of TTotal infections (x-axis) and daily new infections smoothed with moving average (y-axis) on a log-log plot.
This code is to produce Matplotlib figures in svg format embedded in response HTML.
'''

@app.route('/plot_graph3/<name>')
def plot_graph3(name):
    try:
        engine = create_engine(db_uri, echo=False)
        df = pd.read_sql_table(table_name='alberta', con=engine)
        engine.dispose()
        df = df.sort_values(by=['date'])
        df['total_cases'] = df.daily_cases.cumsum()
        df['smooth_daily_cases'] = df.daily_cases.rolling(3).mean()

        fig = Figure()
        FigureCanvas(fig)
        
        fig, (ax) = plt.subplots(nrows=1, ncols=1, sharex=True)
    
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


        img = io.StringIO()
        fig.savefig(img, format='svg')
        #clip off the xml headers from the image
        svg_img = '<svg' + img.getvalue().split('<svg')[1]

    except:
        return render_template('plot.html', name=name, txtx ='', plot='Values not found.')
    else:
        return render_template('plot.html', name=name, txtx ='Total infections (x-axis) and daily new infections smoothed with moving average (y-axis) on a log-log plot', plot=svg_img)


if __name__ == '__main__':
    app.debug = True
    app.run()