import os
import pickle
from collections import Counter

from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


def load_and_split(foldername, num_words):
    ls = os.listdir(foldername)
    X = []
    Y = []
    langmap = dict()
    for idx, x in enumerate(ls):
        print("loading language", x)
        with open(foldername + "/" + x, "r") as reader:
            tmp = reader.read().split(" ")
            tmp = [" ".join(tmp[i : i + num_words]) for i in range(0, 100_000, num_words)]
            X.extend(tmp)
            Y.extend([idx] * len(tmp))
            langmap[idx] = x
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.90)
    return x_train, x_test, y_train, y_test, langmap


def build_and_train_pipeline(x_train, y_train):
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), analyzer="char", use_idf=False)
    clf = Pipeline(
        [
            ("vec", vectorizer),
            # ("nystrom", Nystroem(n_components=1000,n_jobs=6)),
            ("clf", LinearSVC(C=0.5)),
            # ("clf",GaussianNB())
            # ("clf", HistGradientBoostingClassifier())
        ]
    )
    print("fitting model...")
    clf.fit(x_train, y_train)
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
    x_train, x_test, y_train, y_test, langmap = load_and_split(foldername=foldername, num_words=num_words)
    clf = build_and_train_pipeline(x_train, y_train)
    benchmark(clf, x_test, y_test, langmap)
    save_model(clf, langmap, num_words, modelname)
    model = load(modelname)
    print(
        "running inference on long tests",
        inference_voter(
            model,
            """
    What language is this text written in? Nobody knows until you fill in at least ten words.
    This test here is to check whether the moving window approach works,
    so I still need to fill in a little more text.
    """,
        ),
    )


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


def inference_voter(model, text):
    tmp = text.split()
    # print(len(tmp), tmp)
    tmp = [" ".join(tmp[i : i + model["num_words"]]) for i in range(0, len(tmp) - model["num_words"])]
    predictions = model["model"].predict(tmp)
    # print("integer predictions", predictions)
    # print("name predictions", *[model["idx_to_name"][n] for n in predictions])
    result = Counter(predictions).most_common(1)[0][0]
    return model["idx_to_name"][result]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="save location for model and metadata")
    parser.add_argument("-d", "--data", help="specify the folder for data files")
    parser.add_argument("-n", "--num_words", help="number of words to use for statistics", type=int)
    args = parser.parse_args()
    # np.set_printoptions(threshold=np.inf)
    main(args.data, args.model, args.num_words)
