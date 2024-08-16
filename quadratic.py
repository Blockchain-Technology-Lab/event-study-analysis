import numpy as np


def quadratic_order(est_data, obs_data, metric):
    est_predictions = {}
    obs_predictions = {}
    m = np.poly1d(np.polyfit(est_data.index, est_data[metric], 2))
    est_predictions[metric] = m(est_data.index)
    obs_predictions[metric] = m(obs_data.index)
    resid = [m - n for m, n in zip(obs_data[metric].tolist(), obs_predictions[metric])]
    n = len(obs_predictions[metric])
    k = 2
    sse = sum([i ** 2 for i in resid])
    AIC = n*np.log(sse)-n*np.log(n)+2*(k+1)
    return obs_predictions, est_predictions, AIC
