from collections import defaultdict

from flask import Flask, render_template, request, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from model_training.custom_datasets import get_one_dataset
from model_training.dataset_eval.check_if_dataset_is_local import (
    check_if_dataset_is_local,
    ds_mapping,
    get_dataset_counts_from_matched_dict,
)
from model_training.dataset_eval.iterate_over_datasets import iterate_over_dataset
from wtforms import SelectMultipleField, StringField, SubmitField, widgets

# todo: add all datasets
ALL_DATASETS = list(ds_mapping.keys())
# + SUMMARIZATION_DATASETS + OTHER + RL_DATASETS + RM_DATASETS

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


class SearchBarForm(FlaskForm):
    name = StringField("ToSearch")
    submit2 = SubmitField("submit")


# todo: this needs to be configurable
# can be relative or absolute
# "../.cache" also works in my case
cache_dir = "/home/tobias/programming/Open-Assistant/model/model_training/.cache"  # "../.cache"

datasets_dct = dict()
matched = defaultdict(dict)


# check out: https://stackoverflow.com/questions/18290142/multiple-forms-in-a-single-page-using-flask-and-wtforms
@app.route("/", methods=["post", "get"])
def main_page():
    session["counter"] = 0
    session["dropdown_value"] = 10
    ds_form = SimpleForm()
    search_bar_form = SearchBarForm()
    if session.get("dataset_options") is None:
        session["dataset_options"] = [
            c if not check_if_dataset_is_local(c, cache_dir=cache_dir) else f"{c} (local)" for c in ALL_DATASETS
        ]
    ds_form.example.choices = [(c, c) for c in session["dataset_options"]]
    dataset_counts = (
        get_dataset_counts_from_matched_dict(globals()["matched"], session["datasets"])
        if globals().get("matched")
        else list()
    )

    if ds_form.example.data and ds_form.validate_on_submit():
        session["datasets"] = list()
        for dataset_name in ds_form.example.data:
            # todo: allow loading of different modes
            if dataset_name not in session["datasets"]:
                session["datasets"].append(dataset_name)

    if (search_bar_form.name.data and search_bar_form.validate_on_submit()) or globals().get("matched"):
        print("in first stuff")
        if session.get("datasets", {}) == {}:
            print("Please define datasets first")
        else:
            # todo: find better name
            session["search_set"] = True
            processed_text = search_bar_form.name.data
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
                print(f"done loading {dataset_name}")
            global matched
            if dataset_name not in set(matched["train"].keys()).union(matched["val"].keys()):
                for dataset_name, (train, val) in datasets_dct.items():
                    matched["train"][dataset_name] = iterate_over_dataset(
                        train, strings_to_match=[processed_text], regex_strings_to_match=[]
                    )
                    matched["val"][dataset_name] = iterate_over_dataset(
                        val, strings_to_match=[processed_text], regex_strings_to_match=[]
                    )
                dataset_counts = get_dataset_counts_from_matched_dict(matched=matched, datasets=session["datasets"])
    return render_template("base_layout.html", form=ds_form, search_bar_form=search_bar_form, hits=dataset_counts)


@app.route("/datasets/<dataset_name>/<train_or_val>/<keyword>", methods=["post", "get"])
def datasets(dataset_name, keyword, train_or_val):
    ds_form = SimpleForm()
    search_bar_form = SearchBarForm()
    if session.get("dataset_options") is None:
        session["dataset_options"] = [
            c if not check_if_dataset_is_local(c, cache_dir=cache_dir) else f"{c} (local)" for c in ALL_DATASETS
        ]
    hit_lists = list()
    ds_form.example.choices = [(c, c) for c in session["dataset_options"]]
    if (dropdown_value := request.form.get("example_dropdown")) is not None:
        session["dropdown_value"] = dropdown_value

    i = int(session["dropdown_value"])
    hit_lists = (
        matched[train_or_val]
        .get(dataset_name, {})
        .get(keyword, [])[session["counter"] * i : i * (session["counter"] + 1)]
    )

    next_examples = request.form.get("next_examples")
    if next_examples is not None:
        session["counter"] += 1
    return render_template(
        "datasets.html",
        form=ds_form,
        search_bar_form=search_bar_form,
        hits=session.get("dataset_counts", []),
        values=[10, 20, 50],
        dataset_name=dataset_name,
        keyword=keyword,
        train_or_val=train_or_val,
        hit_lists=hit_lists,
    )
