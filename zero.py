import pandas as pd
import numpy as np


def zero_order(est_data, obs_data, metric):
    est_predictions = {}
    obs_predictions = {}
    obs_predictions[metric] = pd.DataFrame(len(obs_data) * [np.mean(est_data[metric])])
    est_predictions[metric] = pd.DataFrame(len(est_data) * [np.mean(est_data[metric])])
    resid = [m - n for m, n in zip(obs_data[metric].tolist(), obs_predictions[metric].iloc[:, 0])]
    n = len(obs_data[metric])
    k = 0
    sse = sum([i ** 2 for i in resid])
    AIC = n * np.log(sse) - n * np.log(n) + 2 * (k + 1)
    return obs_predictions, est_predictions, AIC
