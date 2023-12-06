from flask import Flask, render_template, request
import csv

app = Flask(__name__)

# Define the path to the CSV file
csv_file_path = 'numbers.csv'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the number from the form
        number = request.form['number']

        # Append the number to the CSV file
        with open(csv_file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([number])

    # Read the existing numbers from the CSV file
    existing_numbers = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            existing_numbers.append(row[0])

    return render_template('index.html', existing_numbers=existing_numbers)

if __name__ == '__main__':
    app.run(debug=True)
