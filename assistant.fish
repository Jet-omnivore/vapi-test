#!/opt/homebrew/bin/fish

curl -X PATCH "https://api.vapi.ai/assistant/d9bd023f-b906-4272-86bc-3c7204cd02c5" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hebrew Assistant",
    "transcriber": {
      "provider": "google",
      "model": "gemini-2.5-pro",
      "language": "Multilingual"
    },
    "voice": {
      "provider": "custom-voice",
      "server": {
        "url": "https://e7fe92835cf5.ngrok-free.app/synthesize",
        "timeoutSeconds": 30
      }
    },
    "model": {
      "provider": "openai",
      "model": "gpt-4",
      "messages": [
        {
          "role": "system",
          "content": "You are an advanced and empathetic AI assistant. Your main goal is to sound as human and natural as possible. You speak in Hebrew."
        }
      ]
    },
    "firstMessage": ""
  }'
