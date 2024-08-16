import pandas as pd
from linear import linear_order
from quadratic import quadratic_order
from zero import zero_order
import numpy as np
from netneurotools import stats as nnstats
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

'''
Hi! 

Below is the code to run the event study analysis. The functions for the different models exist in the additional files. 
For more complete context on the project, visit the Notion page which details the proof of concept. 

That said, we have one main problem that we could use help addressing by whomever takes this on next: 
1. We ended up just visualizing the percentage change in the event window. However, the proper way to perform this analysis is to use a permutation test.
The test_significance function relies on a permutation test. We are not sure that this package accomplishes really what we are looking for. 
Ideally, we would follow this algorithm: https://link.springer.com/article/10.1007/s00181-023-02530-7 .... or something similar. 
In short, we need a way to test the significance of the abnormal returns differing from zero which does not rely on the assumption of normality (that a t-test does).
A permutation test is a way to do this. It is important to find single-firm permutation tests, as many tests assume testing an event across multiple firms.
'''


# OPTIONS FOR METRICS "gini", "mpr", "tau", "theil", "nump", "entropy", "hhi", "nc"]


def load_dataframe(coin):
    '''
    :param coin: the name of the coin/.csv file to be imported (.csv file should have the date in rows and the metrics in columns)
    :return: cleaned up pandas dataframe with the date as the index and metrics in columns
    '''
    df = pd.read_csv(f'input/{coin}.csv', header=0)
    df = df.rename(columns={'Unnamed: 0': 'date'})
    df['date'] = pd.to_datetime(df['date'])
    return df

def set_observation_window(df, event_window, days_prior):
    '''
    This function simply helps to return a dataframe of the observation window we specify
    :param df: dataframe in format that is outputted from load_dataframe
    :param event_window: the window that the event occurred in the format of ['yyyy-mm-dd', 'yyyy-mm-dd']
    :param days_prior: how many days before the event start should we build the observation window from
    :return: cleaned up pandas dataframe of data from only the observation window of interest
    '''
    window = df[df["date"].between(datetime.strptime(event_window[0], '%Y-%m-%d') - timedelta(days=days_prior),
                          event_window[0])]
    return window


def pick_best_model(df, event_window, estimated_data, meter):
    '''
    The purpose of this function is to compare 3 different lengths of observation window - 30 days, 60 days and 90 days- along with 3 different models - means, linear and quadratic - to return the combination with the lowest AIC
    :param df: dataframe created by loading function above
    :param event_window: the window that the event occurred in the format of ['yyyy-mm-dd', 'yyyy-mm-dd']
    :param estimated_data: the dataframe only for the dates within the event_window
    :param meter: metric of interest
    :return: AIC = optimized AIC, length of window = length of optimized observation window, esp_to_use = estimation window predictions to use, and the best_name = name of optimized model
    '''
    model_aic = math.inf
    models = {"zero": zero_order, "linear": linear_order,
              "quadratic": quadratic_order}  # dictionary of the model names and their functions
    for days_to_subtract in [30, 60, 90]:
        observed_data = set_observation_window(df, event_window, days_to_subtract)
        for name, fn in models.items():
            obs_preds, est_preds, AIC = fn(estimated_data, observed_data, meter)
            if AIC < model_aic:
                model_aic = AIC
                window = days_to_subtract
                esp_to_use = est_preds
                best_name = name
    return model_aic, window, esp_to_use, best_name

def run_test(coin, meter, event_window):
    df = load_dataframe(coin) #load dataframe
    estimated_data = df[df["date"].between(event_window[0], event_window[1])] #set the estimated data to be the event window specified
    model_aic, window, esp_to_use, best_name = pick_best_model(df, event_window, estimated_data, meter)
    predictions = pd.DataFrame(esp_to_use[meter].values) #reformat the predictions
    predictions = predictions[0].tolist()
    observed = estimated_data[meter].to_list() #reformat the observed data
    difference = np.subtract(observed, predictions)
    abreturns = (np.divide(difference, predictions))*100
    dates = pd.date_range(datetime.strptime(event_window[0], '%Y-%m-%d'),datetime.strptime(event_window[1], '%Y-%m-%d'),freq='d')
    plt.plot(dates, abreturns)
    plt.title(f'{meter}')
    plt.ylabel('% Change')
    plt.show()
    plt.close()

        #if abreturns>0:
            #effect = "positive"
        #if abreturns<0:
            #effect = "negative"
        #if #abreturns == 0:
            #effect = "no effect"
        #if test_significance(abreturns) == True:
            #print(f'{meter}: {best_name} model, {str(window)} day window reveals a significant {effect} event')


def test_significance(abreturns):
    '''
    Using a permutation test, this function determines if the abnormal returns differ significantly from zero.
    :param abreturns: difference between the observed and expected values
    :return: if the results are significant according to the permutation test
    '''
    p = nnstats.permtest_1samp(np.array(abreturns), 0.0)[-1]
    if p > 0.05:
        return False
    if p <0.05:
        return True
run_test("bitcoin", "gini", event_window = ['2022-12-04', '2022-12-09'])


#input metric




