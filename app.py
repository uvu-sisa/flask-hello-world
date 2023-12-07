from flask import Flask, render_template, request
import csv
import plotly.express as px
import plotly.io as pio
import io
from .core import *

app = Flask(__name__)

# Define the path to the CSV file
csv_file_path = 'numbers.csv'

@app.route('/', methods=['GET', 'POST'])
def index():
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
            
    # Read the existing numbers from the CSV file
    existing_numbers = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            existing_numbers.append(row[0])
    pred = np.zeros(NUM_INS)
    if number==37:number='0'
    if number==38:number='00'
    new_df = create_data(number)
    actual_df = write_data(new_df,'actual')
    last_pred = get_last_predictor()
    period_pnl = cal_period_pnl(last_pred,new_df.values.reshape(-1))
    pred = gen_predictor(actual_df)
    write_data(pred,'predictor')
    predT= pred.T
    
    write_pnl(period_pnl)    
    # Sample data
    pnls = pd.read_csv('pnl.csv')
    prediction_list = predT.index.values
    # Create a Plotly Express plot
    fig = px.line(pnls, x="number", y="pnl", title='Cum PNL')

    # Convert the plot to HTML
    plot_html = pio.to_html(fig, full_html=False)
    return render_template('index.html',prediction_list=prediction_list, existing_numbers=existing_numbers,plot_html=plot_html)
