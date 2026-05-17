import os
import json
from groq import Groq

def classify_text(text: str):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {
            "total_score": 0,
            "reasons": ["GROQ_API_KEY is missing"],
            "score_description": "APIキーが設定されていません。",
            "error_message": "GROQ_API_KEY が見つかりません。環境変数を確認してください。"
        }

    client = Groq(api_key=api_key)

    # ★ Groq に「使えるモデル一覧」を問い合わせる
    models = client.models.list()
    available_models = [m.id for m in models.data]

    if not available_models:
        return {
            "total_score": 0,
            "reasons": ["No available models"],
            "score_description": "モデルが利用できないため判定できません。",
            "error_message": "Groq アカウントに利用可能なモデルがありません。"
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
        result = json.loads(content)
    except Exception:
        return {
            "total_score": 0,
            "reasons": ["JSON parse error", content[:200]],
            "score_description": "AI の出力が正しい形式ではありませんでした。",
            "error_message": "⚠️ JSON の解析に失敗しました。通信状況などでまれに発生します。もう一度ボタンを押して再実行してください。"
        }

    # ★ スコア説明を追加
    score_description = {
        0: "安全性が高い投稿です。",
        1: "ほぼ安全ですが、念のため注意してください。",
        2: "やや注意が必要です。",
        3: "少し怪しい要素があります。",
        4: "注意すべきポイントがあります。",
        5: "怪しい要素が複数あります。慎重に判断してください。",
        6: "危険度が高めです。応募は避けた方が良いです。",
        7: "かなり危険です。闇バイトの可能性があります。",
        8: "非常に危険です。絶対に応募しないでください。",
        9: "闇バイトの可能性が極めて高いです。",
        10: "ほぼ確実に闇バイトです。絶対に関わらないでください。"
    }

    result["score_description"] = score_description.get(result["total_score"], "不明")
    result["error_message"] = ""

    return result
