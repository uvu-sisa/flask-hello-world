import numpy as np
import pandas as pd
from flask import Flask, render_template, request
import csv
import plotly.express as px
import plotly.io as pio
import io
import os
'''
new data -> create actual data -> save_actual data -> create prediction -> new data ->save actual data, create pnl -> save pnl
'''
rednums = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
blacknums = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

NUMIX = list(np.arange(1,37))
NUM_MASK = np.zeros(len(NUMIX))
EVENTIX = ['even','odd','black','red','3div','3div1','3div2','L','H',]
EVENT_MASK = np.zeros(len(EVENTIX))
QIX =['1q','2q','3q']
Q_MASK = np.zeros(len(QIX))
ZEROSIX =['0','00']
ZEROS_MASK = np.zeros(len(ZEROSIX))
TICKER = NUMIX+EVENTIX+QIX+ZEROSIX
TICKERIX = np.arange(0,len(TICKER)+1)
NUM_INS = len(TICKER)
RETURNS = [36]*len(NUMIX)+[2]*len(EVENTIX)+[3]*len(QIX)+[18]*len(ZEROSIX)

HL_H = np.arange(19,37)
HL_L = np.arange(1,19)
HLM_L = np.arange(1,13)
HLM_M = np.arange(13,25)
HLM_H = np.arange(25,37)
def get_lh_idx(x):
    if x in HL_H:
        return 1
    return 0
def get_lh(x):
    if x in HL_H:
        return 'High'
    if x in [37]:
        return '0'
    if x in [38]:
        return '00'
    return 'Low'
def get_lmh_idx(x):
    if x in HLM_L:
        return 0
    if x in HLM_M:
        return 1
    if x in HLM_H:
        return 2
    return 0
def get_lmh(x):
    if x in HLM_L:
        return '1st'
    if x in HLM_M:
        return '2nd'
    if x in HLM_H:
        return '3rd'
    if x in [37]:
        return '0'
    if x in [38]:
        return '00'
def get_evenodd(x):
    if x in [37]:
        return '0'
    if x in [38]:
        return '00' 
    if x%2:
        return 'ODD'
    return 'EVEN'
def get_rb(x):
    if x in blacknums:return 'BLACK'
    if x in rednums:return 'BLACK'
    if x in [37]:
        return '0'
    if x in [38]:
        return '00' 
def create_data(x):
    data = np.zeros(len(TICKER))
    print(f'x {x}')
    if str(x) == '0':
        data[-2] = 1
        return pd.DataFrame(data,index=TICKER).T
    if str(x) == '00':
        data[-1] = 1
        return pd.DataFrame(data,index=TICKER).T
    x = int(x)
    data[x-1] = 1 # number
    data[36+x%2] = 1 #event odd
    data[36+2+int(x in (rednums))] = 1 #black n red
    data[36+2+2+x%3] = 1 # div 3
    data[36+2+2+3+get_lh_idx(x)] = 1 # LH
    data[36+2+2+3+2+get_lmh_idx(x)] = 1 # lmh 1q 2q 3q
    
    return pd.DataFrame(data,index=TICKER).T


def write_data(new_df,module_name):
    '''module_name can be actual, prediction'''
    filename = f'{module_name}.csv'
    df = pd.DataFrame()
    if os.path.exists(filename):
        
        df = pd.read_csv(filename).values
        df = np.vstack([df,new_df.values])
    else:
        df = new_df.values
    df = pd.DataFrame(df,columns=TICKER)
    df.to_csv(filename,index=False)
    return df
    
def cal_period_pnl(preds,actual):
    return np.dot(np.multiply(preds,actual),RETURNS)-np.sum(preds)

def write_pnl(period_pnl):
    if os.path.exists('pnl.csv'):
        pnls = pd.read_csv('pnl.csv')
    else: 
        pnls = pd.DataFrame(columns=['pnl'])
    pnls = pd.concat([pnls,pd.DataFrame([period_pnl],columns=['pnl'])])
    pnls.to_csv('pnl.csv',index=False)
    return pnls
    
def get_last_predictor():
    preds =  pd.DataFrame(np.zeros(NUM_INS)[None,:],columns=TICKER)
    if os.path.exists('predictor.csv'):
        preds = pd.read_csv('predictor.csv').iloc[-1]
    return preds
        

def gen_predictor(actual_df,rolling_periods=36,num_bets=3):
    alpha = np.zeros(NUM_INS)
    prob = actual_df.sum()/len(actual_df)
    lst_prob = actual_df.iloc[-rolling_periods:].sum()/rolling_periods
    sum_prob = pd.DataFrame(prob.copy(),columns=['TotalProb'])
    sum_prob[f'Last{rolling_periods}daysProb'] = lst_prob
    sum_prob = sum_prob*100
    sum_prob[['TotalProb',f'Last{rolling_periods}daysProb']] = sum_prob[['TotalProb',f'Last{rolling_periods}daysProb']].astype(int)
    sum_prob.reset_index().to_csv('prob.csv',index=False)
    pred = (prob-lst_prob)*RETURNS
    order_prob = np.argsort(pred.values)
    for i in range(num_bets+1):
        idx = order_prob[-1-i]
        alpha[idx] = 1
    return pd.DataFrame(alpha,index=TICKER).T

    

app = Flask(__name__)

# Define the path to the CSV file
csv_file_path = 'numbers.csv'

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction_list=[]
    compare=None
    if request.method == 'POST':
        
        if 'clear' in request.form:
            # Clear the CSV file
            os.remove('*.csv')
            open(csv_file_path, 'w').close()
            
        else:
            # Get the number from the form and append it to the CSV file
            number = request.form['number']
            with open(csv_file_path, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([number])
            pred = pd.DataFrame(np.zeros(NUM_INS),index=TICKER).T
            if number==37:number='0'
            if number==38:number='00'
            new_df = create_data(number)
            compare = pd.concat([pred,new_df],ignore_index=True).T
            compare.columns=['LastPrediction',f'Actual{number}']
            compare = compare.loc[compare.LastPrediction==1].to_html()
            actual_df = write_data(new_df,'actual')
            last_pred = get_last_predictor()
            period_pnl = cal_period_pnl(last_pred,new_df.values.reshape(-1))
            pred = gen_predictor(actual_df)
            write_data(pred,'predictor')
            predT= pred.T
            prediction_list = ','.join([str(v) for v in list(predT.loc[predT[0]==1].index.values)])
            write_pnl(period_pnl)    
            
    # Read the existing numbers from the CSV file
    existing_numbers = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            existing_numbers.append(row[0])
    
    # Sample data
    if os.path.exists('pnl.csv'):
        pnls = pd.read_csv('pnl.csv')
    else:
        pnls = pd.DataFrame()
    if not pnls.empty:
        # Create a Plotly Express plot
        fig = px.line(pd.read_csv('pnl.csv').cumsum(), title='Cum PNL')
        # Convert the plot to HTML
        plot_html = pio.to_html(fig, full_html=False)
    else:
        plot_html = None
    if os.path.exists('prob.csv'):
        df = pd.read_csv('prob.csv')
        if 'index' not in df.columns:
            df = df.reset_index()
        fig = px.bar(df,x='index' ,y=['TotalProb', 'Last36daysProb'])
        fig.show()
        prob_plot = pio.to_html(fig, full_html=False)
    else:
        prob_plot = None

    return render_template('index.html',compare=compare,prob_plot=prob_plot,prediction_list=prediction_list, 
                           existing_numbers=existing_numbers[::-1],plot_html=plot_html)
