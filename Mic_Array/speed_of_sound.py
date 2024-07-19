


def calculate_speed_of_sound(temperature_F):
    temperature_celsius = (temperature_F - 32) * 5.0 / 9.0
    return 331.3 + 0.606 * temperature_celsius
