from machine import Pin, I2C
from neopixel import NeoPixel
from esp8266_i2c_lcd import I2cLcd
from mfrc522 import MFRC522

# Creamos el Display, primero creamos la conexión I2C
# SDA = D1, SCL = D2 a 400Khz
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# Lector conectado por SPI
# SCK = D5, MOSI = D7, MISO = D6, RST = Rx, CS = SDA = D8
rdr = MFRC522(sck=14, mosi=13, miso=12, rst=16, cs=15)

def read_tag(reader):
    try:
        while True:
            (stat, tag_type) = reader.request(rdr.REQIDL)
            if stat == reader.OK:
                (stat, raw_uid) = rdr.anticoll()
                if stat == reader.OK:
                    print("Card detected")
                    print(" - TAG type: 0x%02x" % tag_type)
                    print(" - ID_TAG: 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                return stat, raw_uid
    except KeyboardInterrupt:
        print('Bye! No card detected')

# # Creamos el solenoide que está en el GPIO16 = D0
# solenoid = Pin(16, Pin.OUT)
# solenoid.off()

# # Creamos el sensor de entrada en el GPIO0 = D3
# input_sensor = Pin(0, Pin.IN)

# # Creamos el sensor de salida en el GPIO2 = D4
# output_sensor = Pin(2, Pin.IN)

# # Creamos el semáforo con el neopixel en el GPIO1 = Tx
# semaforo = NeoPixel(Pin(1), 16)

# for _ in range(8):
#     semaforo[_] = (128, 0, 0)
# for _ in range(8, 16):
#     semaforo[_] = (0, 128, 0)


