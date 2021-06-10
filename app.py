from flask import Flask, render_template, request,send_file
import pandas as pd
import pandas_datareader as pdr
import datetime as dt
app = Flask(__name__)
import os
...
port = int(os.environ.get('PORT', 5000))
...

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hello', methods=['POST'])

@app.route("/files/download", methods=['POST','GET'])
def download():
    first_name = request.form['first_name']
    ticker = first_name
    start = dt.datetime(2018, 1, 1)
    data = pdr.get_data_yahoo(ticker, start)
    data['Signal']=''
    data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
    for i in range(len(data)) :
        if data['Close'][i]>data['EMA20'][i]:
            data['Signal'][i]='buy'
        else:
            data['Signal'][i]='sell'

    sell=0
    buy=0
    for i in range(len(data)):
        if data['Signal'][i]=='sell':
            sell=sell+1
        else:
            buy=buy+1
    data = data.loc['2020-01-01':]
    data = data.iloc[::-1]
    fi=first_name+" "+"REPORT.xlsx"
    writer = pd.ExcelWriter(fi, 
                        engine='xlsxwriter', 
                        date_format = 'yyyy-mm-dd', 
                        datetime_format='yyyy-mm-dd')
    sheet_name = 'Exponential Moving Average'
    data[['Close', 'EMA20','Signal']].to_excel(writer, sheet_name=sheet_name)
    worksheet = writer.sheets[sheet_name]
    workbook = writer.book
    # Create a format for a green cell
    green_cell = workbook.add_format({
    'bg_color': '#C6EFCE',
    'font_color': '#006100'})
    # Create a format for a red cell
    red_cell = workbook.add_format({
    'bg_color': '#FFC7CE',                            
    'font_color': '#9C0006'})
    # Set column width of Date
    worksheet.set_column(0, 0, 15)
    for col in range(1, 4):
        # Create a conditional formatted of type formula
        worksheet.conditional_format(1, col, len(data), col, {
        'type': 'formula',                                    
        'criteria': '=B2>=C2',
        'format': green_cell})
        # Create a conditional formatted of type formula
        worksheet.conditional_format(1, col, len(data), col, {
        'type': 'formula',                                    
        'criteria': '=B2<C2',
        'format': red_cell})
    # Create a new chart object.
    chart1 = workbook.add_chart({'type': 'line'})
    # Add a series to the chart.
    chart1.add_series({
        'name': "Close",
        'categories': [sheet_name, 1, 0, len(data), 0],
        'values': [sheet_name, 1, 1, len(data), 1],})
    # Create a new chart object.
    chart2 = workbook.add_chart({'type': 'line'})
    # Add a series to the chart.
    chart2.add_series({
        'name': 'EMA20',
        'categories': [sheet_name, 1, 0, len(data), 0],
        'values': [sheet_name, 1, 2, len(data),2],})
    # Combine and insert title, axis names
    chart1.combine(chart2)
    chart1.set_title({'name': sheet_name + " " + ticker})
    chart1.set_x_axis({'name': 'Date'})
    chart1.set_y_axis({'name': 'Price'})
    # Insert the chart into the worksheet.
    worksheet.insert_chart('F2', chart1)
    writer.close()
    file_path = fi
    return send_file(
        file_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True)
    return send_file(
        file_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
