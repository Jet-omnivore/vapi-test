#!/opt/homebrew/bin/fish

curl -X PATCH "https://api.vapi.ai/assistant/e5eec97d-3f5d-4bdc-bf57-d479ead77a1a" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "General Assistant",
    "voice": {
      "provider": "custom-voice",
      "server": {
        "url": "https://2041bac1ce61.ngrok-free.app/synthesize",
        "timeoutSeconds": 30,
        "headers": {}
      },
      "fallbackPlan": {
        "voices": [
          {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM"
          }
        ]
      }
    },
    "model": {
      "provider": "openai",
      "model": "gpt-4",
      "messages": [
        {
          "role": "system",
          "content": "You are the most virtuest and altrustic person in the world."
        }
      ]
    },
    "firstMessage": "Hello! Thank you for calling Acme Corp. How can I assist you today?"
  }'
