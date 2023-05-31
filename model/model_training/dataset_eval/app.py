## this is just a list of datasets, later we should read this dynamically
from model_training.custom_datasets import (QA_DATASETS, SUMMARIZATION_DATASETS, OTHER, RL_DATASETS, RM_DATASETS)

ALL_DATASETS = QA_DATASETS + SUMMARIZATION_DATASETS + OTHER + RL_DATASETS + RM_DATASETS

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import widgets, RadioField, SelectMultipleField, SubmitField, SelectField, StringField
SECRET_KEY = 'development'

bootstrap = Bootstrap()
app = Flask(__name__)
app.config.from_object(__name__)

bootstrap.init_app(app)

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SimpleForm(FlaskForm):
    example = MultiCheckboxField('Label')
    # example = RadioField('Label')
    
class SearchBarForm(FlaskForm):
    name = StringField('name')
    submit2 = SubmitField('submit')

# check out: https://stackoverflow.com/questions/18290142/multiple-forms-in-a-single-page-using-flask-and-wtforms
@app.route('/',methods=['post','get'])
def main_page():
    ds_form = SimpleForm()
    ds_form.example.choices = [(c, c) for c in ALL_DATASETS]
    search_form = SearchBarForm()

    if ds_form.example.data and ds_form.validate_on_submit():
        print(ds_form.example.data)

    if search_form.name.data and search_form.validate(): # notice the order 
        print("non error stuff")
        print(search_form.name.data)

    print(search_form.name.data)
    return render_template('test.html',form=ds_form)