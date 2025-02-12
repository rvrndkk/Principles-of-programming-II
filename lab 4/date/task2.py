import datetime

noww = datetime.datetime.now()
beff = noww - datetime.timedelta(days=1)
neww = noww + datetime.timedelta(days=1)

print(beff.date())
print(noww.date())
print(neww.date())