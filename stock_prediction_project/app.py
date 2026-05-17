from flask import Flask, render_template, request
import yfinance as yf

from model import predict_stock

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import mpld3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():

    data = None
    prediction = None
    graph = None
    pie_chart = None
    error = None

    current_price = None
    highest_price = None
    lowest_price = None
    average_price = None
    price_change = None
    trend = None
    suggestion = None
    selected_company = None

    # Company names

    company_names = {

        'AAPL': 'Apple',
        'TSLA': 'Tesla',
        'MSFT': 'Microsoft',
        'GOOGL': 'Google',

        'TCS.NS': 'Tata Consultancy Services',
        'INFY.NS': 'Infosys',
        'RELIANCE.NS': 'Reliance Industries',
        'HDFCBANK.NS': 'HDFC Bank'
    }

    if request.method == 'POST':

        try:

            stock = request.form['stock'].upper()

            selected_company = company_names.get(
                stock,
                stock
            )

            # Download stock data

            stock_data = yf.download(
                stock,
                period='1mo'
            )

            # Fix multi-level columns

            stock_data.columns = stock_data.columns.get_level_values(0)

            # Remove unwanted column name

            stock_data.columns.name = None

            # Invalid stock

            if stock_data.empty:

                error = "Invalid Stock Symbol!"

            else:

                # Reset index

                stock_data.reset_index(inplace=True)

                # CLEAN TABLE

                display_data = stock_data.tail().copy()

                display_data['Open'] = display_data['Open'].astype(float).round(2)

                display_data['High'] = display_data['High'].astype(float).round(2)

                display_data['Low'] = display_data['Low'].astype(float).round(2)

                display_data['Close'] = display_data['Close'].astype(float).round(2)

                display_data = display_data[
                    ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                ]

                data = display_data.to_html(
                    index=False,
                    classes='table',
                    justify='center'
                )

                # Prediction

                prediction = predict_stock(stock)

                # Analytics

                close_prices = stock_data['Close']

                current_price = round(
                    float(close_prices.iloc[-1]),
                    2
                )

                highest_price = round(
                    float(stock_data['High'].max()),
                    2
                )

                lowest_price = round(
                    float(stock_data['Low'].min()),
                    2
                )

                average_price = round(
                    float(close_prices.mean()),
                    2
                )

                old_price = float(close_prices.iloc[0])

                price_change = round(
                    ((current_price - old_price) / old_price) * 100,
                    2
                )

                # Trend analysis

                if price_change > 0:

                    trend = "UPTREND 📈"
                    suggestion = "BUY"

                else:

                    trend = "DOWNTREND 📉"
                    suggestion = "SELL"

                # LINE GRAPH

                plt.figure(figsize=(10, 5))

                plt.plot(
                    stock_data['Date'],
                    close_prices,
                    marker='o'
                )

                plt.title(
                    f"{selected_company} Stock Price"
                )

                plt.xlabel("Date")

                plt.ylabel("Closing Price")

                plt.xticks(rotation=45)

                plt.tight_layout()

                fig = plt.gcf()

                graph = mpld3.fig_to_html(fig)

                plt.close()

                # PIE CHART COMPARISON

                if '.NS' in stock:

                    compare_stocks = [

                        'TCS.NS',
                        'INFY.NS',
                        'RELIANCE.NS',
                        'HDFCBANK.NS'
                    ]

                else:

                    compare_stocks = [

                        'AAPL',
                        'TSLA',
                        'MSFT',
                        'GOOGL'
                    ]

                compare_prices = []
                compare_labels = []

                for s in compare_stocks:

                    temp = yf.download(
                        s,
                        period='1d'
                    )

                    temp.columns = temp.columns.get_level_values(0)

                    temp.columns.name = None

                    close_value = float(
                        temp['Close'].iloc[-1]
                    )

                    compare_prices.append(close_value)

                    compare_labels.append(
                        company_names.get(s, s)
                    )

                # PIE CHART

                plt.figure(figsize=(7, 7))

                plt.pie(
                    compare_prices,
                    labels=compare_labels,
                    autopct='%1.1f%%'
                )

                plt.title(
                    "Stock Market Comparison"
                )

                pie_fig = plt.gcf()

                pie_chart = mpld3.fig_to_html(
                    pie_fig
                )

                plt.close()

        except Exception as e:

            error = str(e)

    return render_template(

        'index.html',

        data=data,
        prediction=prediction,
        graph=graph,
        pie_chart=pie_chart,
        error=error,

        current_price=current_price,
        highest_price=highest_price,
        lowest_price=lowest_price,
        average_price=average_price,
        price_change=price_change,
        trend=trend,
        suggestion=suggestion,
        selected_company=selected_company
    )

if __name__ == '__main__':

    app.run(debug=True)