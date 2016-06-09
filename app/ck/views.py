from flask import render_template
from . import  ck
from ..models import db, Cost

@ck.route('/test')
def test():
    data = {'Chrome': 52.9, 'Opera': 1.6, 'Firefox': 27.7}
    return render_template('ck/test.html', data=data)