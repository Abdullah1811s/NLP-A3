from typing import Union
import pandas as pd
import yfinance as yf

def validate_ticker(ticker: str) -> bool:
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1d")
        return not hist.empty
    except Exception as e:
        print(f"Error validating ticker '{ticker}': {str(e)}")
        return False

def get_structured_data(ticker: str, period: str = "60d") -> Union[pd.DataFrame, None]:
    try:
        ticker_obj = yf.Ticker(ticker)
        hist = ticker_obj.history(period=period)
        hist.reset_index(inplace=True)
        hist = hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        return hist
    except Exception as e:
        print("Error fetching structured data:", e)
        return None

def get_unstructured_data(ticker: str) -> Union[pd.DataFrame, None]:
    try:
        ticker_obj = yf.Ticker(ticker)
        news_list = ticker_obj.news
        if not news_list:
            return None
        
        data = []
        for news in news_list:
            content = news.get('content', {})
            title = content.get('title', 'No title')
            summary = content.get('summary', '')
            link_obj = content.get('clickThroughUrl')
            link = link_obj.get('url') if link_obj else 'No link'
            pub_date = content.get('pubDate', None)
            data.append({
                'published_date': pub_date,
                'title': title,
                'summary': summary,
                'link': link
            })
        
        news_df = pd.DataFrame(data)
        news_df['published_date'] = pd.to_datetime(news_df['published_date'], errors='coerce', utc=True)
        return news_df

    except Exception as e:
        print("Error fetching news:", e)
        return None

def merge_data(hist_df: pd.DataFrame, news_df: pd.DataFrame) -> pd.DataFrame:
    if hist_df is None:
        return news_df
    if news_df is None:
        return hist_df
    
    hist_df['Date'] = pd.to_datetime(hist_df['Date'], errors='coerce', utc=True)
    news_df['published_date'] = pd.to_datetime(news_df['published_date'], errors='coerce', utc=True)
    
    merged = pd.merge_asof(
        news_df.sort_values('published_date'),
        hist_df.sort_values('Date'),
        left_on='published_date',
        right_on='Date',
        direction='backward'
    )
    return merged

def df_to_serializable(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert datetime columns to ISO strings and handle NaT
    """
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']):
        df_copy[col] = df_copy[col].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
    return df_copy

def fetch(ticker: str, period: str = "60d") -> dict:
    if not validate_ticker(ticker):
        return {"success": False, "message": f"Invalid ticker: {ticker}"}
    
    hist_df = get_structured_data(ticker, period=period)
    news_df = get_unstructured_data(ticker)
    merged_df = merge_data(hist_df, news_df)

    if merged_df is not None and not merged_df.empty:
        return {
            "success": True,
            "ticker": ticker,
            "merged_df": df_to_serializable(merged_df).to_dict(orient="records"),
            "hist_df": df_to_serializable(hist_df).to_dict(orient="records") if hist_df is not None else [],
            "news_df": df_to_serializable(news_df).to_dict(orient="records") if news_df is not None else [],
            "rows": len(merged_df)
        }
    else:
        return {"success": False, "message": "No merged data available"}
