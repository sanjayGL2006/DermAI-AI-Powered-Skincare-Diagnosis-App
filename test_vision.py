import os
import requests
import json
import base64

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
model = "gemini-3.6-flash"

with open("test_face.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"

prompt = """You are an expert AI dermatologist. Analyze this facial skin image.
User skin type: Combination. Questionnaire: {}.

Return ONLY valid JSON:
{
  "skin_type":"Normal/Dry/Oily/Combination/Sensitive",
  "conditions_found":[{"name":"...","severity":"mild/moderate/severe","affected_area":"...","confidence":80}],
  "overall_score":70,
  "recommendations":{"creams":[],"soaps":[],"tablets":[],"serums":[],"morning_routine":[],"evening_routine":[]},
  "diet_tips":{"eat":[],"avoid":[]},
  "lifestyle_tips":[],
  "see_doctor":false,
  "doctor_reason":""
}"""

payload = {
    "contents": [
        {
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": img_b64
                    }
                },
                {
                    "text": prompt
                }
            ]
        }
    ],
    "generationConfig": {
        "response_mime_type": "application/json"
    }
}

r = requests.post(url, json=payload, timeout=30)
print("Status code:", r.status_code)
if r.status_code == 200:
    data = r.json()
    text = data['candidates'][0]['content']['parts'][0]['text']
    parsed = json.loads(text)
    print("Parsed JSON successfully!")
    print(json.dumps(parsed, indent=2)[:500])
else:
    print("Error:", r.text)
