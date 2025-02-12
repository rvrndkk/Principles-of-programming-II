import datetime

date1 = datetime.datetime(2025, 1, 1, 12, 0, 0)
date2 = datetime.datetime(2025, 1, 2, 12, 0, 0)

diff = (date2 - date1).total_seconds()
print(diff)
