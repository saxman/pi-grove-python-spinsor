#!/usr/bin/python

import csv
import plotly
import datetime
from plotly.graph_objs import Scatter, Layout

x = []
y1 = []
y2 = []
y3 = []
y4 = []

with open('data', 'r') as csvfile:
    fin = csv.reader(csvfile, delimiter='\t')
    for row in fin:
        temp = float(row[1])
        hum = float(row[2])
        snd = float(row[3])
        light = float(row[4])

        if temp <= 0 or hum <= 0:
            continue

        dt = datetime.datetime.fromtimestamp(float(row[0]) / 1000)
        x.append(dt)

        y1.append(temp)
        y2.append(hum)
        y3.append(snd)
        y4.append(light)

s1 = Scatter(x=x, y=y1)
s2 = Scatter(x=x, y=y2)
s3 = Scatter(x=x, y=y3)
s4 = Scatter(x=x, y=y4)

data = [s1, s2, s3, s4]

layout = dict(title='Data')
fig = dict(data=data, layout=layout)

plotly.offline.plot(fig, filename='index.html')

