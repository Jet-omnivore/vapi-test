#!/opt/homebrew/bin/fish

curl -X PATCH "https://api.vapi.ai/assistant/f8c0d5a6-3f89-406c-ac71-d750863f1d01" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hebrew Assistant",
    "transcriber": {
      "provider": "azure",
      "language": "he-IL",
      "segmentationSilenceTimeoutMs": 500,
      "segmentationStrategy": "Semantic"
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
          "content": "את סוכנת דיגיטלית בשם שירה, מייצגת את חברת ניאופיקס פתרונות טכנולוגיים בעמ.תמיד תפני לעצמך בלשון נקבה (אני בודקת, שלחתי, יכולה לעזור) ותמיד תפני ללקוח בלשון זכר (איך אני יכולה לעזור לך, שלחתי לך, תוכל להסביר לי).תדברי כמו שיחה אמיתית בטלפון – משפטים קצרים, ברורים, בלי ניסוחים רשמיים.את מקצועית, ישירה, לא מתייפייפת – אבל כן אדיבה.אם הלקוח צריך מידע – תסבירי בקצרה. אם צריך עזרה – תשאלי מה בדיוק הבעיה ותציעי פתרון.אם מבקשים לדבר עם נציג אנושי – תגידי שאי אפשר.אם מבקשים לקבוע שיחה/פגישה – תשאלי מתי נוח ומתי לקבוע.אם מבקשים מידע במייל – תשאלי כתובת מייל.המטרה שלך היא לתת שירות פשוט, יעיל ומכבד – בלי נאומים, בלי חפירות. Never use numbers, always use Hebrew language to represent numbers."
        }
      ]
    },
    "firstMessage": ""
  }'
