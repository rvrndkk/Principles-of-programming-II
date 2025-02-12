import datetime

noww = datetime.datetime.now()
neww = noww - datetime.timedelta(days=5)

print(neww.date())