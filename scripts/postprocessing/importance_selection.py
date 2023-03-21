import logging
import warnings

import numpy as np
import pandas as pd
import psycopg2
from scipy.optimize import LinearConstraint, minimize
from scipy.sparse import coo_array, csr_array, csr_matrix, hstack
from scipy.special import softmax
from tqdm import trange
from tqdm.contrib.logging import logging_redirect_tqdm


def least_squares_fit(features, target, scaling=1):
    X = features  # (features - np.mean(features, 0)) / np.std(features, 0)
    # print("feature",X.shape)
    # get target
    y = target.reshape(-1)
    # Use simple imputer for mean to not change the importance of tree split
    # Create an instance of the ExtraTreesRegressor algorithm
    zX = X.toarray()
    summed_target = y  # (y+zX[:,-1])/2
    vote_matrix = csr_matrix(zX[:, :-1])
    constraint = LinearConstraint(np.ones(X.shape[-1] - 1), 1 * scaling, 1 * scaling)
    init = np.ones(X.shape[-1] - 1)  # lsqr(vote_matrix,summed_target)[0]
    init = init / np.linalg.norm(init)
    result = minimize(
        lambda x: np.sum((vote_matrix @ x - summed_target) ** 2),
        init,
        jac=lambda x: 2 * vote_matrix.T @ (vote_matrix @ x - summed_target),
        constraints=constraint,
        hess=lambda _: 2 * vote_matrix.T @ vote_matrix,
        method="trust-constr",
    )
    # result = least_squares(residual, np.ones(X.shape[-1]-1))
    # result = least_squares(zX[:,:-1], (y+zX[:,-1])/2,
    # print(result)
    return np.concatenate([result.x, np.ones(1)])


def get_df(study_label):
    conn = psycopg2.connect("host=0.0.0.0 port=5432 user=postgres password=postgres dbname=postgres")
    # Define the SQL query
    query = (
        "SELECT DISTINCT message_id, labels, message.user_id FROM text_labels JOIN message ON message_id = message.id;"
    )

    # Read the query results into a Pandas dataframe
    df = pd.read_sql(query, con=conn)
    print(df.head())
    # Close the database connection
    conn.close()
    users = set()
    messages = set()
    for row in df.itertuples(index=False):
        row = row._asdict()
        users.add(str(row["user_id"]))
        # for row in df.itertuples(index=False):
        # row = row._asdict()
        messages.add(str(row["message_id"]))
    users = list(users)
    messages = list(messages)
    print("num users:", len(users), "num messages:", len(messages), "num in df", len(df))

    # arr = np.full((len(messages), len(users)), np.NaN, dtype=np.half)
    row_idx = []
    col_idx = []
    data = []

    def swap(x):
        return (x[1], x[0])

    dct = dict(map(swap, enumerate(messages)))
    print("converting messages...")
    df["message_id"] = df["message_id"].map(dct)
    print("converting users...")
    df["user_id"] = df["user_id"].map(dict(map(swap, enumerate(users))))
    print("converting labels...")
    df["labels"] = df["labels"].map(lambda x: float(x.get(study_label, 0)))
    row_idx = df["message_id"].to_numpy()
    col_idx = df["user_id"].to_numpy()
    data = df["labels"].to_numpy()
    print(data)
    print(row_idx)
    print(col_idx)
    """ for row in df.itertuples(index=False):
        row = row._asdict()
        labels = row["labels"]
        value = labels.get(study_label, None)
        if value is not None:
            # tmp=out[str(row["message_id"])]
            # tmp = np.array(tmp)
            # tmp[users.index(row["user_id"])] = value
            # out[str(row["message_id"])] = np.array(tmp)
            # print(out[str(row["message_id"])].density)
            row_idx.append(messages.index(str(row["message_id"])))
            col_idx.append(users.index(str(row["user_id"])))
            data.append(value)
            #arr[mid, uid] = value """
    arr = csr_array(coo_array((data, (row_idx, col_idx))))
    print("results", len(users), arr.shape)
    # df = pd.DataFrame.from_dict(out,orient="index")
    print("generated dataframe")
    return arr, messages, users


def reweight_features(features, weights, noise_scale=0.0):
    # X = df.drop(target_col, axis=1)
    # print("info",features.shape,weights.shape)
    # X = (features - np.mean(features, 0).reshape(1,-1)) / np.std(features, 0).reshape(1,-1)
    noise = np.random.randn(weights.shape[0]) * noise_scale
    weights = weights + noise
    # normalizer = (X.notna().astype(float) * weights).sum(skipna=True, axis=1)
    values = features @ weights
    # values = values / normalizer
    return values


def get_subframe(arr, columns_to_filter):
    # return np.delete(arr, columns_to_filter, axis=1)
    """
    Remove the rows denoted by ``indices`` form the CSR sparse matrix ``mat``.
    """
    if not isinstance(arr, csr_array):
        raise ValueError("works only for CSR format -- use .tocsr() first")
    indices = list(columns_to_filter)
    mask = np.ones(arr.shape[1], dtype=bool)
    mask[indices] = False
    return arr[:, mask]


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
    mask = arr != 0
    to_combine = mask.sum(0) < num_instances
    # print("to combine", mask.sum(0))
    # print("combining", to_combine.astype(int).sum().tolist(), "many columns")
    if not any(to_combine):
        return arr
    # mean = np.zeros(arr.shape[0])
    # for i in to_combine.tolist():
    #    mean = np.nansum(np.stack(arr[:,i],mean),0)
    # mean = mean/len(to_combine)
    mean = np.mean(arr[:, to_combine], 1).reshape(-1, 1)
    # print("mean shape",mean.shape)
    dp = np.arange(len(to_combine))[to_combine]
    # print("removing unused columns")
    arr = get_subframe(arr, dp)
    # print("subframe shape",arr.shape)
    arr = hstack([arr, mean])
    # print("out arr", arr.shape)
    # print((mean==0).astype(int).sum())
    return arr


def importance_votes(arr, to_fit=10, init_weight=None):
    # arr = combine_underrepresented_columns(matrix,underrepresentation_thresh)
    filtered_columns = []
    weighter = None
    if init_weight is None:
        weighter = np.ones(arr.shape[1]) / arr.shape[1]  # pd.Series(1.0, index=df.drop(columns=target).columns)
    else:
        weighter = init_weight
    # print(arr.shape)
    index = np.arange(arr.shape[1])
    # subtract 1: the last one will always have maximal reduction!
    bar = trange(to_fit)
    target = np.ones(arr.shape[0])
    for i in bar:
        index = list(filter(lambda x: x not in filtered_columns, index))
        # 0. produce target column:
        # print("step 0")
        target_old = target
        target = reweight_features(arr, weighter)
        error = np.mean((target - target_old) ** 2)
        bar.set_description(f"expected error: {error}", refresh=True)
        if error < 1e-10:
            break
        # 1. get a subframe of interesting features
        # print("step 1")
        # subframe = get_subframe(arr, filtered_columns)
        # 2. compute feature importance
        # print("step 2")
        # importance_weights=None
        # importance_weights = compute_feature_importance(arr, target, index)
        weighter = least_squares_fit(arr, target)
        # 3. sample column
        # print("step 3")
        # new_column = sample_importance_weights(importance_weights["importance"], temperature)
        # new_column=index[new_column]
        # value = importance_weights["importance"][new_column]
        # print(weighter.shape, importance_weights["importance"].shape)
        # weighter += alpha[i] * importance_weights["importance"].to_numpy()
        # normalize to maintain the "1-voter one vote" total number of votes!
        # weighter = weighter / sum(abs(weighter))
        # stepsize = np.mean(abs(importance_weights["importance"].to_numpy()))
        # bar.set_description(f"expected stepsize: {stepsize}", refresh=True)
        # filtered_columns.append(new_column)
    # print("new weight values", weighter)
    return reweight_features(arr, weighter), weighter


def select_ids(arr, pick_frac, minima=(50, 500), folds=50, to_fit=200, frac=0.6):
    """
    selects the top-"pick_frac"% of messages from "arr" after merging all
    users with less than "minima" votes (minima increases linearly with each iteration from min to max).
    The method returns all messages that are within `frac` many "minima" selection
    """
    votes = []
    minima = np.linspace(*minima, num=folds, dtype=int)
    num_per_iter = int(arr.shape[0] * pick_frac)
    writer_num = 0
    tmp = None
    for i in trange(folds):
        tofit = combine_underrepresented_columns(arr, minima[i])
        if tofit.shape[1] == writer_num:
            print("already tested these writer counts, skipping and using cached value.....")
            votes.append(tmp)
            continue
        writer_num = tofit.shape[1]
        # print("arr shape", arr.shape)
        init_weight = np.ones(tofit.shape[1]) / tofit.shape[1]
        out, weight = importance_votes(tofit, init_weight=init_weight, to_fit=to_fit)
        # print(i, "final weight")
        # print(weight)
        # mask =(out>thresh)
        # out = np.arange(arr.shape[0])[mask]
        indices = np.argpartition(out, -num_per_iter)[-num_per_iter:]
        tmp = np.zeros((arr.shape[0]))
        tmp[indices] = 1
        votes.append(tmp)
        # votes.append(indices.tolist())
    # print(*[f"user_id: {users[idx]} {m}±{s}" for m, s, idx in zip(weights_mean, weights_std, range(len(weights_mean)))], sep="\n")
    out = []
    votes = np.stack(votes, axis=0)
    print("votespace", votes.shape)
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
    df, message_ids, users = get_df("quality")
    print("combining columns:")
    # df = combine_underrepresented_columns(df, 100)
    weights = np.ones(df.shape[-1])
    y = reweight_features(df, weights)
    num_per_iter = int(df.shape[0] * 0.5)
    naive = np.argpartition(y, -num_per_iter)[-num_per_iter:]

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
        ids = select_ids(df, 0.5, folds=500)

    #    print(res, frac)
    conn = psycopg2.connect("host=0.0.0.0 port=5432 user=postgres password=postgres dbname=postgres")
    # Define the SQL query
    # , payload#>'{payload, text}' as text
    query = "SELECT DISTINCT id as message_id, message_tree_id FROM message;"
    print("selected", len(ids), "messages")
    # Read the query results into a Pandas dataframe
    df = pd.read_sql(query, con=conn)
    out = []
    fracs = []
    in_naive = []
    for i, frac in ids:
        res = message_ids[i]
        out.append((df.loc[df["message_id"] == res]))
        fracs.append(frac)
        in_naive.append(i in naive)
    df = pd.concat(out)
    df["fracs"] = fracs
    df["in_naive"] = in_naive
    print(df.shape)
    print("differences from naive", len(in_naive) - sum(in_naive))
    print(df)
    df.to_csv("output.csv")
