import datetime

now = '{d.year}-{d.month}-{d.day}'.format(d=datetime.datetime.now().date())

print(now)
print(type(now))