from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

st.set_page_config(layout='wide', page_title="Stock Analyzer")

# CONSTANTS
END = date.today()
START = END - timedelta(365)

# data handling
def get_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start, end, auto_adjust=False)
        if data.empty:
            return None, f"No data found for {ticker}"
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data, f"Successfully loaded data for {ticker}"
    except Exception as e:
        return None, f"Error {e}"

# sidebar
st.sidebar.title("🗠 Inputs")
ticker = st.sidebar.text_input("Stock symbol", value="AAPL").upper()
comparison_ticker = st.sidebar.text_input("Comparison Ticker", value="SPY")

col1, col2 = st.sidebar.columns(2)
start = col1.date_input("Start Date", value=START)
end = col2.date_input("End Date", value=END)
moving_average = st.sidebar.slider("Moving Average Window",
                                   min_value=10,
                                   max_value=100,
                                   value=50,
                                   step=5)
run = st.sidebar.button("Run Analysis", type='primary')

#main UI
st.title("Stock Analyzer")

if run_button:
    df = get_stock_data(ticker, start_date, end_date)
    comparison_df = get_stock_data(comparison_ticker, start_date, end_date)
  df["normalized_close"] = (df["Close"] / df["Close"].iloc[0]) * 100
comparison_df["normalized_close"] = (comparison_df["Close"] / comparison_df["Close"].iloc[0]) * 100


    if df is not None:
        st.sidebar.success(message)
    else:
        st.sidebar.error(message)
    df['MA'] = df['Close'].rolling(window=moving_average).mean()
    df['pct_change'] = df['Close'].pct_change() * 100

    # output
    tab1, tab2, tab3, tab4 = st.tabs([... , "📈 Comparison"])

    with tab1:
        st.subheader(f"{ticker} High Level Analysis")
        col1, col2, col3 = st.columns(3)
        col1.metric(f'Latest Price', f'{df['Close'].iloc[-1]:.2f}')
        col2.metric(f'Cum Change',
                    f'{((df['Close'].iloc[-1]/df['Close'].iloc[0]) -1) * 100:.2f}')
        col3.metric(f'Trading Days', f'{len(df)}')
        figure = px.line(df, y= ['Close', 'MA'])
        figure.update_layout(hovermode='x unified')
        with st.spinner("Creating chart"):
            st.plotly_chart(figure, use_container_width=True)

    with tab2:
        st.subheader("Summary Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Daily Change Statistics**")
            summary = df['pct_change'].describe()
            st.dataframe(summary)
        with col2:
            price_stats = pd.DataFrame(
                {'Metric': ['High', 'Low', 'Mean', 'Volatility'],
                 'Values': [
                     f"{df["Close"].max()}",
                     f"{df["Close"].min()}",
                     f"{df["Close"].mean()}",
                     f"{df["Close"].std()}"
                 ]
                }
            )
            st.dataframe(price_stats)

    with tab3:
        st.subheader("Raw Data")
        st.dataframe(df.tail(10))
        csv = df.to_csv()
        st.download_button(
                           label="Download Data",
                           data = csv,
                           file_name = f"{ticker}_{start}_{end}.csv",
                           mime="text/csv"
                            )
  
with tab4:
    st.subheader("Comparison (Base 100)")

    plot_df = pd.DataFrame({
        "Date": df.index,
        ticker.upper(): df["normalized_close"].values
    }).merge(
        pd.DataFrame({
            "Date": comparison_df.index,
            comparison_ticker.upper(): comparison_df["normalized_close"].values
        }),
        on="Date",
        how="inner"
    )

    long_df = plot_df.melt(id_vars="Date", var_name="Ticker", value_name="Normalized Close")

    fig = px.line(
        long_df,
        x="Date",
        y="Normalized Close",
        color="Ticker",
        title=f"{ticker.upper()} vs {comparison_ticker.upper()} Performance (Base 100)"
    )

    st.plotly_chart(fig, use_container_width=True)
    summary = pd.DataFrame({
        "Min": [df["normalized_close"].min(), comparison_df["normalized_close"].min()],
        "Max": [df["normalized_close"].max(), comparison_df["normalized_close"].max()],
        "Final": [df["normalized_close"].iloc[-1], comparison_df["normalized_close"].iloc[-1]]
    }, index=[ticker.upper(), comparison_ticker.upper()])

    st.dataframe(summary.style.format("{:.2f}"))
