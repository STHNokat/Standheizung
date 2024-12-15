import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import ssl
import requests
import threading
from datetime import datetime

# MQTT-Konfiguration
MQTT_SERVER = "MQTT-HOST"
MQTT_PORT = 8883
MQTT_USER = "USER"
MQTT_PASSWORD = "PASSWORT"
MQTT_TOPIC_CONTROL = "home/standheizung/control"

# Relais GPIO Pins
RELAY_PIN_1 = 9
RELAY_PIN_2 = 10

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN_1, GPIO.OUT)
GPIO.setup(RELAY_PIN_2, GPIO.OUT)
GPIO.output(RELAY_PIN_1, GPIO.HIGH)
GPIO.output(RELAY_PIN_2, GPIO.HIGH)

# MQTT-Client Setup
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

mqtt_client.tls_set()
mqtt_client.tls_insecure_set(False)

mqtt_client.connect(MQTT_SERVER, MQTT_PORT, 60)

#Define Startstatus
heizung_status = "STOP"

# Funktion zum Starten der Heizung
def start_heizung():
    print("Heizung startet...")
    GPIO.output(RELAY_PIN_1, GPIO.LOW)
    time.sleep(1)  # Relais für 1 Sekunde anziehen
    GPIO.output(RELAY_PIN_1, GPIO.HIGH)
    mqtt_client.publish("home/standheizung/status", "START", retain=True) #Status in MQTT veröffentlichen

# Funktion zum Stoppen der Heizung
def stop_heizung():
    print("Heizung stoppt...")
    GPIO.output(RELAY_PIN_2, GPIO.LOW)
    time.sleep(1)  # Relais für 1 Sekunde anziehen
    GPIO.output(RELAY_PIN_2, GPIO.HIGH)
    mqtt_client.publish("home/standheizung/status", "STOP", retain=True) #Status in MQTT veröffnetlichen

# Funktion zum Senden von Webhook-POST-Anfragen
def send_webhook(url):
    payload = {'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    try:
        response = requests.post(url, json=payload)
        print(f"Webhook sent: {response.status_code}")
    except Exception as e:
        print(f"Webhook failed: {e}")

# MQTT Callback Funktionen
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing to the control topic
    client.subscribe(MQTT_TOPIC_CONTROL)

def on_message(client, userdata, msg):
    global heizung_status
    if msg.topic == MQTT_TOPIC_CONTROL:
        payload = msg.payload.decode()
        if payload == "START":
            start_heizung()
            heizung_status = "START"
            send_webhook("WEBHOOK-URL")
        elif payload == "STOP":
            stop_heizung()
            heizung_status= "STOP"
            send_webhook("WEBHOOK-URL")
        print(f"Heizung-Status geändert: {heizung_status}")

# MQTT Setup
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.loop_start()

# Funktion zum automatischen Wiederaktivieren des Relais alle 32 Minuten, wenn die Heizung an ist
def periodic_heizung_relay():
    while True:
        time.sleep(32 * 60)  # Alle 32 Minuten
        if heizung_status == "START":
            start_heizung()  # Wiederhole den Relais-Anzug
            send_webhook("WEBHOOK-URL")

# Starten der Überwachung
try:
    periodic_heizung_thread = threading.Thread(target=periodic_heizung_relay)
    periodic_heizung_thread.daemon = True
    periodic_heizung_thread.start()

    # Hauptloop für MQTT-Verbindung
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Programm beendet.")
    GPIO.cleanup()
