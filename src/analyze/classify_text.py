import subprocess
import json
import sys
import io

# Windows の標準出力を UTF-8 に強制
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def classify_text(text: str):
    # プロンプト読み込み
    with open("models/prompt_classifier.txt", "r", encoding="utf-8") as f:
        prompt = f.read().replace("{{POST_TEXT}}", text)

    # Ollama 実行（ストリームではなく一括で受け取る）
    result = subprocess.run(
        ["ollama", "run", "qwen2.5:7b-instruct"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8"
    )

    output = result.stdout.strip()

    if not output:
        return {
            "total_score": 0,
            "reasons": ["empty output", "no response from model"]
        }

    # JSON としてパース
    try:
        return json.loads(output)
    except Exception as e:
        return {
            "total_score": 0,
            "reasons": ["JSON parse error", str(e), output[:200]]
        }
