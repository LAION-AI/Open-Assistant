## this is just a list of datasets, later we should read this dynamically
from model_training.custom_datasets import OTHER, QA_DATASETS, RL_DATASETS, RM_DATASETS, SUMMARIZATION_DATASETS
from model_training.dataset_eval.iterate_over_datasets import iterate_over_dataset
from collections import defaultdict
from itertools import islice

# todo: add all datasets
ALL_DATASETS = [
    "webgpt",
    "soda",
    "dolly15k",
    "soda_dialogue",
    "jokeexplaination",
]  # + SUMMARIZATION_DATASETS + OTHER + RL_DATASETS + RM_DATASETS

from flask import Flask, render_template, request, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from model_training.custom_datasets import get_one_dataset
from model_training.dataset_eval.check_if_dataset_is_local import check_if_dataset_is_local
from wtforms import RadioField, SelectField, SelectMultipleField, StringField, SubmitField, widgets

SECRET_KEY = "development"

bootstrap = Bootstrap()
app = Flask(__name__)
app.config.from_object(__name__)

bootstrap.init_app(app)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SimpleForm(FlaskForm):
    example = MultiCheckboxField("Label")
    # example = RadioField('Label')


class SearchBarForm(FlaskForm):
    name = StringField("name")
    submit2 = SubmitField("submit")


# todo: this needs to be configurable
cache_dir = "../.cache"

datasets_dct = dict()
matched = defaultdict(dict)


# check out: https://stackoverflow.com/questions/18290142/multiple-forms-in-a-single-page-using-flask-and-wtforms
@app.route("/", methods=["post", "get"])
def main_page():
    ds_form = SimpleForm()
    search_bar_form = SearchBarForm()
    if session.get("dataset_options") is None:
        session["dataset_options"] = [
            c if not check_if_dataset_is_local(c, cache_dir=cache_dir) else f"{c} (local)" for c in ALL_DATASETS
        ]
    ds_form.example.choices = [(c, c) for c in session["dataset_options"]]
    dataset_counts = list()

    if ds_form.example.data and ds_form.validate_on_submit():
        session["datasets"] = list()
        for dataset_name in ds_form.example.data:
            # todo: allow loading of different modes
            if dataset_name not in session["datasets"]:
                session["datasets"].append(dataset_name)
        print(ds_form.example.data)

    if search_bar_form.name.data and search_bar_form.validate_on_submit():
        if session.get("datasets", {}) == {}:
            # todo: display
            print("Please define datasets first")
        else:
            # todo: find better name
            session["search_set"] = True
            processed_text = search_bar_form.name.data
            print(processed_text)
            global datasets_dct
            for dataset_name in session["datasets"]:
                if dataset_name not in datasets_dct:
                    train, val = get_one_dataset(
                        None, dataset_name.replace(" (local)", ""), mode="sft", data_path=cache_dir
                    )
                    if val is not None:
                        ds_tuple = (train, val)
                    else:
                        ds_tuple = (train, train)
                    datasets_dct[dataset_name] = ds_tuple

            for dataset_name, (train, val) in datasets_dct.items():
                global matched
                print(dataset_name)
                matched["train"][dataset_name] = iterate_over_dataset(
                    train, strings_to_match=[processed_text], regex_strings_to_match=[]
                )
                matched["val"][dataset_name] = iterate_over_dataset(val, strings_to_match=[processed_text], regex_strings_to_match=[])
                train_dct = {k: len(v) for k, v in matched["train"][dataset_name].items()}
                val_dct = {k: len(v) for k, v in matched["val"][dataset_name].items()}
                # todo: this needs to be inside the loop
                dataset_counts.extend(
                    [
                        {
                            "dataset_name": dataset_name,
                            "train_val": "train",
                            "keyword": processed_text,
                            "hits": train_dct.get(processed_text, 0),
                        },
                        {
                            "dataset_name": dataset_name,
                            "train_val": "val",
                            "keyword": processed_text,
                            "hits": val_dct.get(processed_text, 0),
                        },
                    ]
                )
                session["dataset_counts"] = dataset_counts

    # return render_template("test.html", form=ds_form)
    return render_template("base_layout.html", form=ds_form, search_bar_form=search_bar_form, hits=dataset_counts)


@app.route("/datasets/<dataset_name>/<train_or_val>/<keyword>", methods=["post", "get"])
def datasets(dataset_name, keyword, train_or_val):
    ds_form = SimpleForm()
    print(f"this is the keyword {keyword}, {train_or_val}")
    search_bar_form = SearchBarForm()
    if session.get("dataset_options") is None:
        session["dataset_options"] = [
            c if not check_if_dataset_is_local(c, cache_dir=cache_dir) else f"{c} (local)" for c in ALL_DATASETS
        ]
    hit_lists = list()
    ds_form.example.choices = [(c, c) for c in session["dataset_options"]]
    dataset_counts = list()
    dropdown_value = request.form.get("example_dropdown")
    if dropdown_value is not None:
        tt = matched[train_or_val].get(dataset_name, {}).get(keyword, [])[:int(dropdown_value)]
        hit_lists = tt
        print(tt)
        print(tt[0])
        # train_vals = matched["train"].get(dataset_name)
        # print("This is train_vals")
        # print(train_vals)
        # print("DUMMPY")
        # keys = train_vals.keys()
        # print(keys)
        #kk = list(keys)[:int(dropdown_value)]
        # print(f"dropdown value: {dropdown_value} and type: {type(dropdown_value)}")
        # print(list(islice(train_vals.items(), int(dropdown_value))))
        # print(list(islice(train_vals, 50)))
        # print(len(list(islice(train_vals, 50))))
    print(dropdown_value)
    return render_template(
        "datasets.html",
        form=ds_form,
        search_bar_form=search_bar_form,
        hits=session.get("dataset_counts", []),
        values=[10, 20, 50],
        dataset_name=dataset_name,
        keyword=keyword, 
        train_or_val=train_or_val,
        hit_lists=hit_lists
    )
