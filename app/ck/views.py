from flask import render_template
from . import  ck
from ..models import db, Cost

@ck.route('/test')
def test():
    data = {'Chrome': 52.9, 'Opera': 1.6, 'Firefox': 27.7}
    # data = [{'data': [['2013-04-01 00:00:00 UTC', 52.9], ['2013-05-01 00:00:00 UTC', 50.7]], 'name': 'Chrome'},
    # {'data': [['2013-04-01 00:00:00 UTC', 27.7], ['2013-05-01 00:00:00 UTC', 25.9]], 'name': 'Firefox'}]
    return render_template('ck/test.html', data=data)


@ck.route('/label_pie')
def label_pie():
    label_dict = {}
    label_data = db.session.execute('select label_name,sum(cost_money) from thing_cost join cost_label on thing_cost.label_id=cost_label.label_id group by label_name;').fetchall()
    for data in label_data:
        label_dict[data[0]]= round(data[1], 2)
    return render_template('ck/label_pie.html', label_dict = label_dict)


# @ck.route('/dept_pie')
# def