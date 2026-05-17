import json
from groq import Groq

# Groq APIキーを環境変数に入れておく
# Streamlit Cloud → Secrets に GORQ_API_KEY を設定
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def classify_text(text: str):
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
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    # JSONとしてパース
    try:
        return json.loads(content)
    except Exception:
        # JSONが壊れていた場合の保険
        return {
            "total_score": 0,
            "reasons": ["JSON parse error", content[:200]]
        }
