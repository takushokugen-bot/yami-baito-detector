import os
import json
from groq import Groq

def classify_text(text: str):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {
            "reasons": ["GROQ_API_KEY is missing"],
            "error_message": "GROQ_API_KEY が設定されていません。環境変数を確認して、もう一度押してください。"
        }

    client = Groq(api_key=api_key)

    # ★ Groq に「使えるモデル一覧」を問い合わせる
    models = client.models.list()
    available_models = [m.id for m in models.data]

    if not available_models:
        return {
            "reasons": ["No available models"],
            "error_message": "利用可能なモデルがありません。もう一度押してください。"
        }

    # ★ llama 系を優先、なければ最初のモデル
    target_model = next((m for m in available_models if "llama" in m.lower()), available_models[0])

    # ★ スコアなし版プロンプト（理由3つだけ返す）
    prompt = f"""
以下の文章を闇バイト危険度として判定し、必ず JSON のみを返してください。

【絶対ルール】
- JSON の外に一文字でも出さない
- 説明文・前置き・補足は禁止
- コードブロック禁止
- 理由は必ず3つ返す
- 出力は JSON のみ

文章:
{text}

出力形式:
{{
  "reasons": ["理由1", "理由2", "理由3"]
}}
"""

    response = client.chat.completions.create(
        model=target_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = response.choices[0].message.content

    # ★ JSON のみ返ってくる前提で parse
    try:
        result = json.loads(content)
    except Exception:
        return {
            "reasons": ["JSON parse error"],
            "error_message": "⚠️ AI の出力が正しい形式ではありませんでした。通信状況などでまれに発生します。もう一度押してください。"
        }

    # ★ 正常時は error_message を空にして返す
    result["error_message"] = ""
    return result
