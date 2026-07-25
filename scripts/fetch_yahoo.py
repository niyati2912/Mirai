import yfinance as yf

ASSETS = {
    "sp500": "^GSPC",
    "nasdaq": "^IXIC",

    #indiaa
    "nifty50": "^NSEI",
    "sensex": "^BSESN",


    "gold": "GC=F",
    "silver": "SI=F",
    "oil": "CL=F",
    "brent_oil": "BZ=F",
    "dollar_index": "DX-Y.NYB",
}
#this code line i sasking the yahoo finannce to give me the daily data of sandp 500 of 10 years
#there is no api key cuz yfinance uses publicly avail data
#gspc is a ticker symbol yahoo has assets w specific ticker symbols 

for filename, ticker in ASSETS.items():

    print(f"Downloading {filename}...")

    df = yf.download(
        ticker,
        period="10y",
        auto_adjust=True,
        progress=False
    )

    df.to_csv(f"data/raw/{filename}.csv")

