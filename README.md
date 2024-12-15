# Standheizung

## Vorbereitungen
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
