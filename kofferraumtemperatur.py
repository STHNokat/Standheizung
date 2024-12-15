import paho.mqtt.client as mqtt
import time
import json
from w1thermsensor import W1ThermSensor

# Sensor-Setup
sensor = W1ThermSensor()

mqtt_broker = "MQTT-HOST"
mqtt_port = 8883
mqtt_user = "USER"
mqtt_password = "PASSWORT"
mqtt_topic_state = "homeassistant/sensor/kofferaumtemperature/state"
mqtt_topic_config = "homeassistant/sensor/kofferaumtemperature/config"

# MQTT-Setup
mqtt_client = mqtt.Client(client_id="KofferaumTemperaturePublisher", userdata=None, protocol=mqtt.MQTTv311)
mqtt_client.username_pw_set(mqtt_user, mqtt_password)
mqtt_client.tls_set()  # SSL aktivieren
mqtt_client.connect(mqtt_broker, mqtt_port)

# MQTT Discovery-Nachricht senden
discovery_payload = {
    "device_class": "temperature",
    "state_topic": "homeassistant/sensor/kofferaumtemperature/state",
    "unit_of_measurement": "°C",
    "value_template": "{{ value_json.temperature }}",
    "unique_id": "temp_kofferraum_01",
    "device": {
        "identifiers": ["kofferraum_01"],
        "name": "Kofferaum Temperatur",
        "manufacturer": "Example sensors Ltd.",
        "model": "Example Sensor",
        "model_id": "K9",
        "serial_number": "12AE3010545",
        "hw_version": "1.01a",
        "sw_version": "2024.1.0",
        "configuration_url": "https://example.com/sensor_portal/config"
    }
}

mqtt_client.publish(mqtt_topic_config, json.dumps(discovery_payload), qos=1, retain=True)

# Temperatur auslesen und senden
while True:
    temperature = sensor.get_temperature()
    
    # MQTT-Nachricht mit Temperaturwert senden
    payload = {
        "temperature": temperature
    }
    
    mqtt_client.publish(mqtt_topic_state, json.dumps(payload), qos=1, retain=True)
    print(f"Kofferaum Temperatur gesendet: {temperature}°C")
    
    time.sleep(60)  # Alle 60 Sekunden senden
