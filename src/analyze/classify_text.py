import os
import json
from groq import Groq

def classify_text(text: str):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {
            "理由": ["GROQ_API_KEY が設定されていません。"],
            "メッセージ": "もう一度押してください。"
        }

    client = Groq(api_key=api_key)

    # モデル一覧取得
    models = client.models.list()
    available_models = [m.id for m in models.data]

    if not available_models:
        return {
            "理由": ["利用可能なモデルがありません。"],
            "メッセージ": "もう一度押してください。"
        }

    # llama 系優先
    target_model = next((m for m in available_models if "llama" in m.lower()), available_models[0])

    # 理由だけ返すプロンプト
    prompt = f"""
以下の文章を闇バイト危険度として判定し、必ず JSON のみを返してください。

【絶対ルール】
- JSON の外に一文字も出さない
- 説明文・前置き・補足は禁止
- コードブロック禁止
- 理由は必ず3つ返す
- 出力は JSON のみ

文章:
{text}

出力形式:
{{
  "理由": ["理由1", "理由2", "理由3"]
}}
"""

    response = client.chat.completions.create(
        model=target_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = response.choices[0].message.content

    # JSON parse
    try:
        result = json.loads(content)
        result["メッセージ"] = ""
        return result

    except Exception:
        return {
            "理由": ["AI の出力が正しい形式ではありませんでした。"],
            "メッセージ": "通信状況などでまれに発生します。もう一度押してください。"
        }
