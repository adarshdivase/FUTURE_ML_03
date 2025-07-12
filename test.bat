@echo off
echo Starting Rasa shell...

set RASA_TELEMETRY_ENABLED=false
set TF_CPP_MIN_LOG_LEVEL=2

rasa shell
