import logging
import warnings

import numpy as np
import pandas as pd
import psycopg2
import shap
from scipy.special import softmax
from scipy.stats import dirichlet
from tqdm import trange
from tqdm.contrib.logging import logging_redirect_tqdm
from xgboost import XGBRegressor


def get_df(study_label):
    conn = psycopg2.connect("host=0.0.0.0 port=5432 user=postgres password=postgres dbname=postgres")
    # Define the SQL query
    query = "SELECT message_id, labels, message.user_id FROM text_labels JOIN message ON message_id = message.id;"

    # Read the query results into a Pandas dataframe
    df = pd.read_sql(query, con=conn)
    print(df.head())
    # Close the database connection
    conn.close()
    users = set()
    for row in df.itertuples(index=False):
        row = row._asdict()
        users.add(str(row["user_id"]))
    users = list(users)
    messages = set()
    for row in df.itertuples(index=False):
        row = row._asdict()
        messages.add(str(row["message_id"]))
    messages = list(messages)

    arr = np.full((len(messages), len(users)), np.NaN, dtype=np.half)

    for row in df.itertuples(index=False):
        row = row._asdict()
        labels = row["labels"]
        value = labels.get(study_label, None)
        if value is not None:
            # tmp=out[str(row["message_id"])]
            # tmp = np.array(tmp)
            # tmp[users.index(row["user_id"])] = value
            # out[str(row["message_id"])] = np.array(tmp)
            # print(out[str(row["message_id"])].density)
            mid = messages.index(str(row["message_id"]))
            uid = users.index(str(row["user_id"]))
            arr[mid, uid] = value
    print("results", len(users), arr.shape)
    # df = pd.DataFrame.from_dict(out,orient="index")
    print("generated dataframe")
    return arr, messages


def compute_feature_importance(features, target, index):
    """
    Computes feature importance weights using the Extra Trees algorithm.

    Args:
        df (pandas.DataFrame): An DataFrame of input features.
        target (string): Column which contains the labels.

    Returns:
        dict: A dictionary mapping feature names to importance weights.
    """
    # get rid of target
    X = (features - np.nanmean(features, 0)) / np.nanstd(features, 0)
    # print("feature",X.shape)
    # get target
    y = target
    # Use simple imputer for mean to not change the importance of tree split
    # Create an instance of the ExtraTreesRegressor algorithm
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    et = XGBRegressor(tree_method="gpu_hist", n_estimators=200, verbosity=0)
    # et =
    # now get wether the coefficient is negative or positive:
    # lin = Pipeline([("scaler", StandardScaler()),("imputer", SimpleImputer(missing_values=np.nan, strategy='constant',fill_value=0)), ("lin", LinearRegression())])

    # Fit the algorithm to the input data
    et.fit(X, y)
    # lin.fit(X, y)

    # Get the feature importances from the fitted algorithm
    # importances = np.array(list(et.named_steps["extra trees"].get_booster().get_score(importance_type="gain").values()))

    explainer = shap.Explainer(et, verbosity=0)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    shap_values = explainer.shap_values(X)
    # Normalize based on _non NAN_ features:
    mask = ~np.isnan(X)
    to_combine = mask.sum(0) + 1
    importances = np.sum(shap_values, 0) / to_combine

    # print(len(importances),len(coefficient),X.columns.tolist())
    # Create a dictionary mapping feature names to importance weights
    # print("index",len(index))
    # print("length importance", importances)
    # print("length coefficient", len(coefficient))

    importance_series = pd.DataFrame({"importance": importances}, index=index)
    return importance_series


def reweight_features(features, weights):
    # X = df.drop(target_col, axis=1)
    # print("info",features.shape,weights.shape)
    X = (features - np.nanmean(features, 0, keepdims=True)) / np.nanstd(features, 0, keepdims=True)
    # print(X.shape, weights.shape)
    # normalizer = (X.notna().astype(float) * weights).sum(skipna=True, axis=1)
    values = np.nansum(X * weights.reshape(1, -1), axis=1)
    # values = values / normalizer
    return values


def get_subframe(arr, columns_to_filter):
    return np.delete(arr, columns_to_filter, axis=1)


def sample_importance_weights(importance_weights, temperature=1.0):
    weights = softmax(
        abs(importance_weights) / temperature,
    )
    column = np.random.choice(len(importance_weights), p=weights)
    return column


def make_random_testframe(num_rows, num_cols, frac_missing):
    data = np.random.rand(num_rows, num_cols).astype(np.float16)
    mask = np.random.rand(num_rows, num_cols) < frac_missing
    data[mask] = np.nan
    return data


def combine_underrepresented_columns(arr, num_instances):
    # 1. get the mask
    mask = ~np.isnan(arr)
    to_combine = mask.sum(0) < num_instances
    print("to combine", mask.sum(0))
    print("combining", to_combine.astype(int).sum().tolist(), "many columns")
    if not any(to_combine):
        return arr
    # mean = np.zeros(arr.shape[0])
    # for i in to_combine.tolist():
    #    mean = np.nansum(np.stack(arr[:,i],mean),0)
    # mean = mean/len(to_combine)
    mean = np.nanmean(arr[:, to_combine], 1, keepdims=True)
    print(mean.shape)
    dp = np.arange(len(to_combine))[to_combine]
    print("removing unused columns")
    arr = get_subframe(arr, dp)
    arr = np.concatenate([arr, mean], 1)
    print("out arr", arr.shape)
    print(np.isnan(mean).astype(int).sum())
    return arr


def importance_votes(arr, alpha=100.0, to_fit=50, init_weight=None):
    # arr = combine_underrepresented_columns(matrix,underrepresentation_thresh)
    filtered_columns = []
    weighter = None
    if init_weight is None:
        weighter = np.ones(arr.shape[1])  # pd.Series(1.0, index=df.drop(columns=target).columns)
    else:
        weighter = init_weight
    index = list(range(arr.shape[1]))
    # subtract 1: the last one will always have maximal reduction!
    bar = trange(to_fit)
    for _ in bar:
        index = list(filter(lambda x: x not in filtered_columns, index))
        # 0. produce target column:
        # print("step 0")
        target = reweight_features(arr, weighter)
        # 1. get a subframe of interesting features
        # print("step 1")
        # subframe = get_subframe(arr, filtered_columns)
        # 2. compute feature importance
        # print("step 2")
        importance_weights = compute_feature_importance(arr, target, index)
        # 3. sample column
        # print("step 3")
        # new_column = sample_importance_weights(importance_weights["importance"], temperature)
        # new_column=index[new_column]
        # value = importance_weights["importance"][new_column]
        # print(weighter.shape, importance_weights["importance"].shape)
        weighter += alpha * importance_weights["importance"].to_numpy()
        # normalize to maintain the "1-voter one vote" total number of votes!
        stepsize = np.mean(abs(importance_weights["importance"].to_numpy()))
        bar.set_description(f"expected stepsize: {stepsize}", refresh=True)
        weighter = weighter / sum(abs(weighter)) * len(weighter)
        # filtered_columns.append(new_column)
    # print("new weight values", weighter)
    return reweight_features(arr, weighter), weighter


def select_ids(arr, pick_frac, alph_range=(100, 100), folds=20, frac=0.5):
    # votes = []
    votes = np.zeros((folds, len(arr)))
    alphas = np.geomspace(alph_range[0], alph_range[1], folds)
    num_per_iter = int(len(arr) * pick_frac)
    for i in trange(folds):
        tofit = np.copy(arr)
        # print("arr shape", arr.shape)
        init_weight = dirichlet.rvs(np.ones(arr.shape[1]))[0]
        out, weight = importance_votes(tofit, alpha=alphas[i], init_weight=init_weight)
        print(i, "final weight")
        print(weight)
        # mask =(out>thresh)
        # out = np.arange(arr.shape[0])[mask]
        indices = np.argpartition(out, -num_per_iter)[-num_per_iter:]
        votes[i, indices] = 1
        # votes.append(indices.tolist())
    out = []
    votes = np.mean(votes, 0)
    for idx, f in enumerate(votes):
        if f > frac:
            out.append((idx, f))
    return out


LOG = logging.getLogger(__name__)

if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.simplefilter("ignore")
    logging.captureWarnings(True)
    logging.basicConfig(level=logging.ERROR)
    # Generate some example data
    # df = make_random_testframe(100_000,5000,0.99)
    df, message_ids = get_df("spam")
    print("combining columns:")
    df = combine_underrepresented_columns(df, 250)

    print("after preprocessing")
    # print(df)
    # preproc input

    # Compute feature importances
    # y = reweight_features(df,np.ones(df.shape[1]))
    # importance_weights = compute_feature_importance(df, y, list(range(df.shape[1])))
    # Print the importance weights for each feature
    # print(importance_weights)

    print("STARTING RUN")

    # sampled_columns = sample_importance_weights(
    #    importance_weights["importance"],
    # )
    # print("sampled column", sampled_columns)
    # print("compute importance votes:")
    # weighted_votes, weightings = importance_votes(df)
    # print(weighted_votes)
    # print(weightings)
    with logging_redirect_tqdm():
        print("selected ids")
    ids = select_ids(df, 0.1)
    for i, frac in ids:
        res = message_ids[i]
        print(res, frac)
