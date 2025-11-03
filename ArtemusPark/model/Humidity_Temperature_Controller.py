import random

class Humidity_Temperature_Controller:
    def humidity(self):
        humidity = random.randint(0,100)
        if humidity<30.00:
            print(f"Humidity it is low {humidity}")
        elif humidity<70.00:
            print(f"Humidity it is high {humidity}")
        else:
            print(f"Humidity it is {humidity}")

    def temperature(self):
        temperature = random.randint(-5,40)
        if temperature>30.00:
            print(f"The weather it is heat {temperature}º")
        elif temperature<15.00:
            print(f"The weather it is cold {temperature}º")
