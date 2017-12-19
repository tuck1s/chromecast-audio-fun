# chromecast-audio-fun
Python experiments with sending live-ish audio to ChromeCast device

1. Start the webserver with
```bash
export FLASK_APP=audioserver.py
flask run --host=0.0.0.0 --port=8080 --debugger
```

2. Start the cast with
```bash
python3 startStream.py
```
