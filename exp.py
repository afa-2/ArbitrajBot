from datetime import datetime
ts = float('1687264572855')

# if you encounter a "year is out of range" error the timestamp
# may be in milliseconds, try `ts /= 1000` in that case
print(datetime.fromtimestamp(ts))
datetime(2007, 3, 4, 0, 46, 43, 100000)