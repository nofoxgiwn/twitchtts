#!/bin/bash
curl -X POST http://localhost:5000/tts -H 'Content-Type: application/json' -d \
'{ "speaker_id": "32", "speech_speed": "1.1", "speech_var_a": "0.345", "speech_var_b": "0.5", "text": "Wenn du das hörst, dann funktioniert alles einwandfrei.", "playback": true}'