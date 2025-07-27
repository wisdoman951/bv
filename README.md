# bv

## signal_collector.py

This script monitors the table at <https://agile-cliffs-23967.herokuapp.com> every minute. When a row meets the conditions `Pings >= 5` and `Net Vol % >= 3`, it fetches the current price from the Binance Futures API, calculates stop loss and take profit levels and logs the signal to `signals_log.xlsx`.

### Requirements

```
pip install -r requirements.txt
```

### Usage

Run the script with Python 3:

```
python signal_collector.py
```

The browser runs headlessly and keeps the page open while checking the data periodically.
