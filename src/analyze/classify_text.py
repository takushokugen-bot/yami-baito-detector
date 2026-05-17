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

    # 利用可能モデル一覧を取得
    models = client.models.list()
    available_models = [m.id for m in models.data]

    if not available_models:
        return {
            "total_score": 0,
            "reasons": ["No available models in your Groq account"]
        }

    # llama を優先
    target_model = next((m for m in available_models if "llama" in m.lower()), available_models[0])

    # ★ user メッセージ 1 個だけにする（Groq の分類モデル仕様）
    prompt = f"""
以下の文章を闇バイト危険度として判定し、必ず JSON のみを返してください。
説明文・前置き・補足は禁止。コードブロックも禁止。

文章:
{text}

出力形式:
{{
  "total_score": 数値,
  "reasons": ["理由1", "理由2"]
}}
"""

    response = client.chat.completions.create(
        model=target_model,
        messages=[
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
