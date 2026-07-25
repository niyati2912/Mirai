import yfinance as yf

sp500 = yf.download("^GSPC", period="10y")
#this code line i sasking the yahoo finannce to give me the daily data of sandp 500 of 10 years
#there is no api key cuz yfinance uses publicly avail data
#gspc is a ticker symbol yahoo has assets w specific ticker symbols 


sp500.to_csv("data/raw/sp5000.csv", index=True )

print("save successfully")