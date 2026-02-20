import network
import socket
from machine import Pin, PWM
import time

# --- Pin Definitions ---
AIN1 = Pin(26, Pin.OUT)
AIN2 = Pin(25, Pin.OUT)
PWMA = PWM(Pin(33), freq=1000)

BIN1 = Pin(14, Pin.OUT)
BIN2 = Pin(12, Pin.OUT)
PWMB = PWM(Pin(13), freq=1000)

STDBY = Pin(27, Pin.OUT)

# --- Network & UDP Config ---
#SSID = "NAME_OF_AP"
#PASSWORD = "PASSWORD_AP"
UDP_PORT = 4210

def setup_sta():
    """Configures the ESP32 to connect to your home Wi-Fi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('CharviA', 'ageu6718')
    
    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
        
    ip_address = wlan.ifconfig()[0]
    print("Connected! New IP Address:", ip_address)
    return wlan

# --- Motor Control Functions ---
def run_motor(motor, spd, direction):
    STDBY.value(1)  # Take motor driver out of standby
    
    dir_pin1 = 0    # LOW
    dir_pin2 = 1    # HIGH

    if direction == 1:
        dir_pin1 = 1
        dir_pin2 = 0

    # MicroPython uses 16-bit resolution for PWM (0 - 65535)
    # We map the 0-255 speed from your C++ code to 0-65535
    duty_cycle = int((spd / 255.0) * 65535)

    if motor == 0:  # Motor A
        AIN1.value(dir_pin1)
        AIN2.value(dir_pin2)
        PWMA.duty_u16(duty_cycle)
    else:           # Motor B
        BIN1.value(dir_pin1)
        BIN2.value(dir_pin2)
        PWMB.duty_u16(duty_cycle)

def move_left(spd):
    run_motor(0, spd, 0)
    run_motor(1, spd, 1)

def move_right(spd):
    run_motor(0, spd, 1)
    run_motor(1, spd, 0)

def move_forward(spd):
    run_motor(0, spd, 0)
    run_motor(1, spd, 0)

def move_back(spd):
    run_motor(0, spd, 1)
    run_motor(1, spd, 1)

def stop():
    STDBY.value(0)  # Put motor driver in standby
    PWMA.duty_u16(0)
    PWMB.duty_u16(0)

# --- Main Initialization & Loop ---
def main():
    setup_sta()
    
    # Setup UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', UDP_PORT))
    # Setting a timeout replaces the need for the delay(100) in Arduino
    # If no data arrives in 100ms, it triggers an OSError.
    sock.settimeout(0.1) 
    print("UDP server started on port", UDP_PORT)

    while True:
        try:
            data, addr = sock.recvfrom(255)
            # Decode the bytes received into a string, then to an integer
            try:
                fingers_extended = int(data.decode('utf-8').strip())
                print("Received fingers:", fingers_extended)

                if fingers_extended == 0:
                    stop()
                    print("Stop")
                elif fingers_extended == 1:
                    move_forward(255)
                    print("Forward")
                elif fingers_extended == 2:
                    move_back(255)
                    print("Back")
                elif fingers_extended == 3:
                    move_left(255)
                    print("Left")
                elif fingers_extended == 4:
                    move_right(255)
                    print("Right")
                else:
                    stop()
                    print("Stop")

            except ValueError:
                # Handle cases where non-integer data is sent
                print("Invalid data received")
                stop()

        except OSError:
            # This triggers if sock.recvfrom() times out (no data in 0.1s)
            stop()
            print("Data not received")

if __name__ == "__main__":
    main()

