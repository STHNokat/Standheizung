# Standheizung

## Vorbereitungen
### Aufbau
#### Verbaute Teile
1. Raspberry Pi 2
2. 2-Kanal Relais
3. DS18B20 Thermomether
4. SIM7600X LTE Modul

#### Verdrahtung
##### Raspberry
1. SIM7600 per USB -> Raspberry
2. 2-Kanal Relais:
VCC -> 5v Raspi
GND -> GND
In1 -> Pin 9 Raspi
IN2 -> Pin 10 Raspi
3. DS18B20
VCC -> 5V Raspi
GND -> GND
Data -> GPIO4
PullUP Widerstand - 4,7kOHM zwischen VCC und Data
##### Fernbedienung
Gehäuse außeinander bauen, Adeckung der Tasten abnehmen - Kabel an die zwei Schalter löten und jeweils einen Schalter mit einem Relais verbinden

#### Gehäuse
Per Onshape designed und 3D-gedruckt

### Konfiguration LTE Modul
#### Raspberry vorbereiten
``sudo raspi-config``
Interface Options → Serial Port
Would you like a login shell to be accessible over serial? → Nein
Would you like the serial port hardware to be enabled? → Ja

#### Modem prüfen
``ls /dev/ttyUSB*``
Ausgabe sollte ttyUSB2 oder ttyS0 anzeigen

#### Serielle Konsole aktivieren
``minicom -D /dev/ttyUSB2``

#### Eingaben
```
AT //prüft Modem Kommunikation
OK

AT+COPS=0 // stellt die Netzwerk Registrierung auf automatisch
OK

AT+CREG=1
OK

AT+CGATT=1 // Verbindung zum Packet Domain Service
OK

AT+CGDCONT=<cid>,"IP","wsim"
OK
```

#### Internetzugang einrichten
``sudo apt-get install wvdial``
``sudo nano /etc/wvdial.conf``
```
[Dialer Defaults]
Modem = /dev/ttyUSB2
Modem Type = USB Modem
Baud = 115200
Init = ATZ
Init2 = AT+CFUN=1
ISDN = 0
Phone = *99#
Username = <leer lassen>
Password = <leer lassen>
Stupid Mode = 1
Dial Command = ATDT
```

``sudo nano /etc/ppp/peers/wvdial``
```
noauth
name wvdial
usepeerdns
defaultroute
replacedefaultroute
```

#### Datenverbindung starten
```
sudo wvdial
sudo route add -net "0.0.0.0" ppp0
```

### SystemD-Jobs
#### 1. Standheizung
``nano /etc/systemd/system/standheizung.service``
```
[Unit]
Description=Standheizung MQTT Control
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/lennard/standheizungnew.py
WorkingDirectory=/home/lennard
Restart=always
User=lennard
Group=lennard

[Install]
WantedBy=multi-user.target
```

#### 2. Thermomether
``nano /etc/systemd/system/thermo.service``
```
[Unit]
Description=Thermo Sensor Service
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/lennard
User=lennard
Environment=PATH=/home/lennard/myenv/bin:/usr/bin:/usr/local/bin
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/lennard/myenv/bin/python3 /home/lennard/thermo.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. LTE Starten
``nano /etc/systemd/system/wvdial.service``
```
[Unit]
Description=WVDial LTE Connection
After=network.target dev-ttyUSB2.device
Requires=dev-ttyUSB2.device

[Service]
Type=simple
ExecStart=/bin/bash -c "sleep 10 && /usr/bin/wvdial"
Restart=always
User=root
StandardOutput=journal
StandardError=journal
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 4. SSH Reverse Host
``nano /etc/systemd/system/reverse-ssh.service``
```
[Unit]
Description=Reverse SSH Tunnel to VPS
After=network.target

[Service]
User=lennard
ExecStartPre=/bin/sleep 60
ExecStart=/usr/bin/ssh -N -R 2222:localhost:22 root@ÖFFENTLICHESERVERIP
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Cronjobs
#### Sicherheitsscript
``sudo crontab - e``
``*/5 * * * * /usr/local/bin/connection-check.sh``
