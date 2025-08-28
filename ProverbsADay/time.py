import time
ask = input()
time_1 = time.strftime("%Y-%m-%d")
while True:
    ask = input()
    time_2 = time.strftime("%Y-%m-%d")
    if time_1 == time_2:
        print('Wait a day')
    else:
        print('Here you go')

