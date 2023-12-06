from flask import Flask, render_template, request
import csv
import plotly.express as px
import plotly.io as pio
import io

app = Flask(__name__)

# Define the path to the CSV file
csv_file_path = 'numbers.csv'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'clear' in request.form:
            # Clear the CSV file
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
    
    # Sample data
    df = px.data.iris()

    # Create a Plotly Express plot
    fig = px.scatter(df, x='sepal_width', y='sepal_length', color='species', size='petal_length')

    # Convert the plot to HTML
    plot_html = pio.to_html(fig, full_html=False)
    return render_template('index.html', existing_numbers=existing_numbers,plot_html=plot_html)
