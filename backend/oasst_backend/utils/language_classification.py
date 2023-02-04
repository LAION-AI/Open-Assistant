import json
import os
import pickle
from collections import Counter

from sklearn import metrics
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC


def load_and_split(foldername, num_words, whitelist):
    ls = os.listdir(foldername)
    X = []
    Y = []
    langmap = dict()
    idx = 0
    for x in ls:
        if whitelist is not None:
            if x in whitelist:
                whitelist.remove(x)
            else:
                continue
        print("loading language", x)
        idx += 1
        with open(foldername + "/" + x, "r") as reader:
            tmp = reader.read().split(" ")
            tmp = [" ".join(tmp[i : i + num_words]) for i in range(0, 100_000, num_words)]
            X.extend(tmp)
            Y.extend([idx] * len(tmp))
            langmap[idx] = x
    print("remaining languages", whitelist)
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.80)
    return x_train, x_test, y_train, y_test, langmap


def build_and_train_pipeline(x_train, y_train):
    vectorizer = TfidfVectorizer(ngram_range=(1, 3), analyzer="char", use_idf=False)
    print(len(x_train))
    clf = Pipeline(
        [
            ("vec", vectorizer),
            (
                "dim_reduction1",
                TruncatedSVD(
                    50,
                    n_iter=10,
                ),
            ),
            ("standardization", StandardScaler()),
            # ("transform",PolynomialCountSketch(n_components=400)),
            # ("nystrom", Nystroem(n_components=1000)),
            # penalty="l1",dual=False,tol=1e-3
            ("clf", LinearSVC(C=0.5, max_iter=10_000, tol=1e-3)),
            # ("clf",GaussianNB())
            # ("clf", HistGradientBoostingClassifier(max_iter=100))
        ]
    )
    print("fitting model...")
    clf.fit(x_train, y_train)
    print("fitted model with sparsity degree of", (clf["clf"].coef_ == 0).mean())
    # clf["clf"].sparsify()
    return clf


def benchmark(clf, x_test, y_test, langmap):
    print("benchmarking model...")
    y_pred = clf.predict(x_test)
    names = list(langmap.values())
    # print(y_test)
    # print(langmap)
    print(metrics.classification_report(y_test, y_pred, target_names=names))
    cm = metrics.confusion_matrix(y_test, y_pred)
    print(cm)


def main(foldername, modelname, num_words):
    whitelist_language = [
        "English",
        "Bengali",
        "German",
        "Spanish",
        "French",
        "Hungarian",
        "Japanese",
        "Portuguese",
        "Russian",
        "Vietnamese",
        "Chinese",
    ]
    x_train, x_test, y_train, y_test, langmap = load_and_split(
        foldername=foldername, num_words=num_words, whitelist=whitelist_language
    )
    clf = build_and_train_pipeline(x_train, y_train)
    import time

    t = time.time()
    benchmark(clf, x_test, y_test, langmap)
    print("Ours time taken", time.time() - t)
    save_model(clf, langmap, num_words, modelname)
    model = load(modelname)
    print(
        "running infernence on long tests",
        inference_voter(
            model,
            """
    What language is this text written in? Nobody knows until you fill in at least ten words.
    This test here is to check whether the moving window approach works,
    so I still need to fill in a little more text.
    """,
        ),
    )
    return model


def load(modelname):
    with open(modelname, "rb") as writer:
        data = pickle.load(writer)
    return data


def save_model(model, idx_to_name, num_words, modelname):
    out = {
        "model": model,
        "idx_to_name": idx_to_name,
        "num_words": num_words,
    }
    with open(modelname, "wb") as writer:
        pickle.dump(out, writer)


def inference_voter(model, text, converter=None):
    tmp = text.split()
    # print(len(tmp), tmp)
    tmp = [" ".join(tmp[i : i + model["num_words"]]) for i in range(0, len(tmp) - model["num_words"])]
    if len(tmp) <= model["num_words"]:
        return None, 0
    predictions = model["model"].predict(tmp)
    # print("integer predictions", predictions)
    # print("name predictions", *[model["idx_to_name"][n] for n in predictions])
    result = Counter(predictions).most_common(1)[0]
    if converter is None:
        return model["idx_to_name"][result[0]], result[1] / len(tmp)
    return converter[model["idx_to_name"][result[0]]], result[1] / len(tmp)


def infere_names(model, json_path, converter):
    with open(json_path, "r") as json_file:
        json_list = list(json_file)
    correction_results = []
    corrected_json = []
    for json_str in json_list:
        print("step")
        js = json.loads(json_str)
        js, reps = helper(model, js, converter)
        # print(reps)
        correction_results.extend(reps)
        corrected_json.append(js)
    return corrected_json, correction_results


def helper(model, js, converter):
    if js.get("prompt", None) is not None:
        return helper(model, js["prompt"], converter=converter)
    elif js.get("replies", None) is not None:
        # print("replies path")
        # print(js["text"])
        # print("checking text:",js["text"])
        lang, confidence = inference_voter(model, js["text"], converter=converter)
        tmp = [
            {
                "predicted lang": lang,
                "confidence": confidence,
                "expected lang": js["lang"],
                "message_id": js["message_id"],
                "text": js["text"],
            }
        ]
        reps = []
        for j in js["replies"]:
            dc, ls = helper(model, j, converter=converter)
            reps.append(dc)
            tmp = tmp + ls
        js["lang"] = lang if lang is not None else js["lang"]
        js["replies"] = reps
        return js, tmp
    else:
        return js, []


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model", help="save location for model and metadata")
    parser.add_argument(
        "-t",
        "--test_data",
        help="json file containing test data",
    )
    parser.add_argument("-l", "--load", help="load model instead of training one", action="store_true")
    parser.add_argument("-d", "--data", help="specify the folder for data files")
    parser.add_argument("-n", "--num_words", help="number of words to use for statistics", type=int)
    args = parser.parse_args()
    # np.set_printoptions(threshold=np.inf)
    model = None
    if not args.load:
        model = main(args.data, args.model, args.num_words)
    else:
        model = load(args.model)
    converter = {
        "English": "en",
        "Bengali": "bn",
        "German": "de",
        "Spanish": "es",
        "French": "fr",
        "Hungarian": "hu",
        "Japanese": "ja",
        "Portuguese": "pt-BR",
        "Russian": "ru",
        "Vietnamese": "vi",
        "Chinese": "zh",
    }
    corrected_json, correction_results = infere_names(model, args.test_data, converter)
    for m in correction_results:
        if m["predicted lang"] != m["expected lang"] and m["predicted lang"] is not None:
            print(
                "mismatch",
                m["predicted lang"],
                m["expected lang"],
                m["message_id"],
                m["confidence"],
                m["text"][:50].replace("\n", "\\n"),
            )
