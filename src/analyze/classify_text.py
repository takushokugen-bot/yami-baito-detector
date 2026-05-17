import os
import json
from groq import Groq

def classify_text(text: str):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {
            "total_score": 0,
            "reasons": ["GROQ_API_KEY is missing"]
        }

    client = Groq(api_key=api_key)

    prompt = f"""
あなたは「闇バイト募集文の危険度を判定するAI」です。
以下の文章を読み、JSON形式で返してください。

文章:
{text}

出力フォーマット（必ずこの形式で返す）:
{{
  "total_score": 数値（0〜100）,
  "reasons": [
      "理由1",
      "理由2",
      "理由3"
  ]
}}
"""

    response = client.chat.completions.create(
        model="llama3-8b",
        messages=[
            {"role": "system", "content": "あなたは危険度を判定するAIです。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except Exception:
        return {
            "total_score": 0,
            "reasons": ["JSON parse error", content[:200]]
        }
