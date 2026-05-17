import os

# 自動生成するフォルダ一覧
folders = [
    "data/raw_posts",
    "data/images",
    "data/logs",
    "src/fetch",
    "src/analyze",
    "src/dashboard",
    "src/utils",
    "config",
    "models",
    "scripts"
]

for f in folders:
    if not os.path.exists(f):
        os.makedirs(f)
        print(f"Created: {f}")
    else:
        print(f"Exists: {f}")
