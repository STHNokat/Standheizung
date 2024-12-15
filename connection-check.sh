#!/bin/bash

logfile="/var/log/connection-check.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$logfile"
}

log "Starte Verbindungstest..."

if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    log "Ping erfolgreich. Keine Aktion erforderlich."
    exit 0
else
    log "Ping fehlgeschlagen. Neustart von wvdial.service..."
    systemctl restart wvdial.service
    sleep 10

    log "Neustart von thermo.service und standheizung.service..."
    systemctl restart thermo.service
    systemctl restart standheizung.service
    sleep 5

    log "Erneuter Verbindungstest nach Dienstneustart..."
    if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        log "Verbindung wiederhergestellt."
        exit 0
    else
        log "Verbindung immer noch fehlgeschlagen. Raspberry wird neu gestartet."
        reboot
    fi
fi
