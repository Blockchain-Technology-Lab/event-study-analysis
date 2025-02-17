import os
import pandas as pd
from linear import linear_order
from quadratic import quadratic_order
from zero import zero_order
import numpy as np
from netneurotools import stats as nnstats
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


# OPTIONS FOR METRICS "gini", "mpr", "tau", "theil", "nump", "entropy", "hhi", "nc"]


def load_dataframe(ledger):
    """
    :param ledger: the name of the ledger/.csv file to be imported (.csv file should have the date in rows and the metrics in columns)
    :return: cleaned up pandas dataframe with the date as the index and metrics in columns
    """
    df = pd.read_csv(f'input/{ledger}.csv', header=0)
    df = df.rename(columns={'Unnamed: 0': 'date'})
    df['date'] = pd.to_datetime(df['date'])
    return df


def set_observation_window(df, event_start_date, days_prior):
    """
    This function simply helps to return a dataframe of the observation window we specify
    :param df: dataframe in format that is outputted from load_dataframe
    :param event_start_date: the first day of the event window, in the format of 'yyyy-mm-dd'
    :param days_prior: how many days before the event start should we build the observation window from
    :return: cleaned up pandas dataframe of data from only the observation window of interest
    """
    window = df[df["date"].between(datetime.strptime(event_start_date, '%Y-%m-%d') - timedelta(days=days_prior),
                                   event_start_date)]
    return window


def pick_best_model(df, event_window, estimated_data, meter):
    """
    The purpose of this function is to compare 3 different lengths of observation window - 30 days, 60 days and 90
    days - along with 3 different models - means, linear and quadratic - to return the combination with the lowest AIC
    :param df: dataframe created by loading function above
    :param event_window: the window that the event occurred in the format of ['yyyy-mm-dd', 'yyyy-mm-dd']
    :param estimated_data: the dataframe only for the dates within the event_window
    :param meter: metric of interest
    :return: model_aic = optimized AIC, window = length of optimized observation window, esp_to_use = estimation
    window predictions to use, best_name = name of optimized model
    """
    model_aic = math.inf
    models = {"zero": zero_order, "linear": linear_order,
              "quadratic": quadratic_order}  # dictionary of the model names and their functions
    for days_to_subtract in [30, 60, 90]:
        observed_data = set_observation_window(df, event_window[0], days_to_subtract)
        for name, fn in models.items():
            obs_preds, est_preds, AIC = fn(estimated_data, observed_data, meter)
            if AIC < model_aic:
                model_aic = AIC
                window = days_to_subtract
                esp_to_use = est_preds
                best_name = name
    return model_aic, window, esp_to_use, best_name


def run_test(ledger, meter, event_window):
    df = load_dataframe(ledger)
    estimated_data = df[
        df["date"].between(event_window[0], event_window[1])]  # set the estimated data to be the event window specified
    model_aic, window, esp_to_use, best_name = pick_best_model(df, event_window, estimated_data, meter)
    predictions = pd.DataFrame(esp_to_use[meter].values)  # reformat the predictions
    predictions = predictions[0].tolist()
    observed = estimated_data[meter].to_list()  # reformat the observed data
    difference = np.subtract(observed, predictions)
    abreturns = (np.divide(difference, predictions)) * 100
    dates = pd.date_range(datetime.strptime(event_window[0], '%Y-%m-%d'),
                          datetime.strptime(event_window[1], '%Y-%m-%d'), freq='d')
    plt.plot(dates, abreturns)
    plt.title(f'{meter}')
    plt.ylabel('% Change')
    plt.show()
    plt.savefig(f'output/{ledger}_{meter}_{event_window[0]}_{event_window[1]}.png')
    plt.close()

    # if abreturns > 0:
    #     effect = "positive"
    # if abreturns < 0:
    #     effect = "negative"
    # if abreturns == 0:
    #     effect = "no effect"
    # if test_significance(abreturns) is True:
    #     print(f'{meter}: {best_name} model, {str(window)} day window reveals a significant {effect} event')


def test_significance(abreturns):
    """
    Using a permutation test, this function determines if the abnormal returns differ significantly from zero.
    :param abreturns: difference between the observed and expected values
    :return: if the results are significant according to the permutation test
    """
    p = nnstats.permtest_1samp(np.array(abreturns), 0.0)[-1]
    return p < 0.05


output_dir = 'output/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
run_test("bitcoin", "gini", event_window=['2022-12-04', '2022-12-09'])
