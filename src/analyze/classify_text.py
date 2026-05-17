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

    # ★ 安定版プロンプト（JSON固定・理由3つ・キー順固定）
    prompt = f"""
以下の文章を闇バイト危険度として判定し、必ず JSON のみを返してください。

【絶対ルール】
- JSON の外に一文字でも出さない
- 説明文・前置き・補足は禁止
- コードブロック禁止
- キーの順序は "total_score" → "reasons"
- 理由は必ず3つ返す
- 出力は JSON のみ

文章:
{text}

出力形式:
{{
  "total_score": 数値,
  "reasons": ["理由1", "理由2", "理由3"]
}}
"""

    response = client.chat.completions.create(
        model=target_model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,  # ★ 揺れを完全に抑える
    )

    content = response.choices[0].message.content

    # ★ JSON のみ返ってくる前提で parse
    try:
        return json.loads(content)
    except Exception:
        return {
            "total_score": 0,
            "reasons": ["JSON parse error", content[:200]]
        }
