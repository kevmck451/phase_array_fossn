




import bme280
import smbus2
from time import sleep


def get_temp():
    port = 3
    address = 0x76
    bus = smbus2.SMBus(port)

    bme280.load_calibration_params(bus, address)

    bme280_data = bme280.sample(bus, address)
    # date = bme280_data.timestamp.split(" ")[0]
    # time = bme280_data.timestamp.split(' ')[0].split('+')[0].split('.')[0] # need to correct time zone
    # humidity = int(bme280_data.humidity)
    ambient_temperature = int((bme280_data.temperature * 9 / 5) + 32)

    return ambient_temperature



def example_code():
    port = 3
    address = 0x76
    bus = smbus2.SMBus(port)

    bme280.load_calibration_params(bus,address)

    while True:
        bme280_data = bme280.sample(bus,address)
        # date = bme280_data.timestamp.split(" ")[0]
        # time = bme280_data.timestamp.split(' ')[0].split('+')[0].split('.')[0] # need to correct time zone
        humidity  = int(bme280_data.humidity)
        ambient_temperature = int((bme280_data.temperature * 9/5) + 32)
        print(f'\tTemp: {ambient_temperature} F\t|\tHumid: {humidity} %')
        sleep(1)


if __name__ == '__main__':
    example_code()








