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

    # ★ Groq に「使えるモデル一覧」を問い合わせる
    models = client.models.list()
    available_models = [m.id for m in models.data]

    if not available_models:
        return {
            "total_score": 0,
            "reasons": ["No available models in your Groq account"]
        }

    # ★ llama 系を優先、なければ最初のモデル
    target_model = next((m for m in available_models if "llama" in m.lower()), available_models[0])

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
        model=target_model,
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
