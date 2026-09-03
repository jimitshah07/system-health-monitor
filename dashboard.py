# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 15:35:17 2026

@author: Jimit Shah
"""

"""FOR FLASK"""

from flask import Flask,render_template
import os
import csv
from collections import deque

app=Flask(__name__)

CSV_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'system_health_log.csv')

def get_latest_stats():
    with open(CSV_FILE,mode="r") as f:
        reader=csv.DictReader(f)
        last_row=deque(reader,maxlen=1)
    return last_row[0] if last_row else None

@app.route('/')
def home():
    stats=get_latest_stats()
    return render_template('dashboard.html', stats=stats)

if __name__=="__main__":
    app.run(debug=True,use_reloader=False)
    