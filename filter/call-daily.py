import daily
import schedule
import configparser
import time

config_temp = configparser.RawConfigParser()
config_temp.read('filter_config.cfg')
configs = dict(config_temp.items('DAILY_READINGS'))
print(configs)
times = configs['time'].split(",")
print(times)

for hour in times:
    print(hour)
    schedule.every().day.at(hour).do(daily.main)

#schedule.every(30).seconds.do(daily.main)
#daily.main()

while True :
    schedule.run_pending()
    time.sleep(1)




#Every day at 12am or 00:00 time bedtime() is called.
#schedule.every().day.at("00:00").do(go_to_bed)
