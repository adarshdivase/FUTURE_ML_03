@echo off
echo Starting Rasa training...

set RASA_TELEMETRY_ENABLED=false
set TF_CPP_MIN_LOG_LEVEL=2

echo Training model (this may take a few minutes)...
rasa train --verbose

echo Training completed!
echo To test your bot, run: rasa shell
echo To test NLU only, run: rasa shell nlu
pause
