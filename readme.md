To convert output raw pcm data to wav file use this command:
```curl -X POST \
                                                                     -H 'Content-Type: application/json' \
                                                                     -d '{"message": { "type": "voice-request", "text": "Hello, I am Avinash", "sampleRate": 24000}}' \
                                                                     -o output.pcm http://0.0.0.0:8000/synthesize```
```ffmpeg -f s16le -ar 24k -i [input-file] [output-file]```
