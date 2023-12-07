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
    
    if str(x) == '0':
        data[-2] = 1
        return pd.DataFrame(data,index=TICKER).T
    if str(x) == '00':
        data[-1] = 1
        return pd.DataFrame(data,index=TICKER).T
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
    return np.dot(np.multiply(preds,actual),RETURNS)

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
    pred = (prob-lst_prob)*RETURNS
    order_prob = np.argsort(pred.values)
    for i in range(num_bets+1):
        idx = order_prob[-1-i]
        alpha[idx] = 1
    return pd.DataFrame(alpha,index=TICKER).T

    
