import sqlite3
import json
from flask import render_template
from . import monitor


conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

@monitor.route('/memory')
def mermory():
    return render_template('monitor/memory.html')


@monitor.route('/data')
def data():
    sql = 'select * from m'