import network
import socket
from machine import Pin, PWM
import time

# --- Pin Definitions ---
AIN1 = Pin(25, Pin.OUT)
AIN2 = Pin(33, Pin.OUT)
BIN1 = Pin(27, Pin.OUT)
BIN2 = Pin(14, Pin.OUT)
PWMA = Pin(32, Pin.OUT)
PWMB = Pin(12, Pin.OUT)
STBY = Pin(26, Pin.OUT)

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
PWMA.on()
PWMB.on()
STBY.on()

def move_left():
    AIN1.off(); AIN2.on()
    BIN1.on(); BIN2.off()

def move_right():
    AIN1.on(); AIN2.off()
    BIN1.off(); BIN2.on()

def move_forward():
    AIN1.on(); AIN2.off()
    BIN1.on(); BIN2.off()

def move_back():
    AIN1.off(); AIN2.on()
    BIN1.off(); BIN2.on()

def stop():
    AIN1.off(); AIN2.off()
    BIN1.off(); BIN2.off()

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

