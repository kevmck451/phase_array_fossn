import bme280
import smbus2
from time import sleep


port = 3
address = 0x76
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

while True:
    bme280_data = bme280.sample(bus,address)
    date = bme280_data.timestamp.split(" ")[0]
    time = bme280_data.timestamp.split(' ')[0].split('+')[0].split('.')[0] # need to correct time zone
    humidity  = int(bme280_data.humidity)
    ambient_temperature = int((bme280_data.temperature - 32) * 5.0 / 9.0)
    print(f'Temp: {ambient_temperature} F\t|\tHumid: {humidity} %')
    sleep(1)