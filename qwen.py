# qwen.py
import base64
import csv
import os
import time
import requests

# ========== 修正后的关键参数 ==========
TEST_CSV   = r"D:\Desktop\作品\2025\2025讯飞系列\复杂图文的逻辑推理挑战赛\test.csv"
IMAGE_DIR  = r"D:\Desktop\作品\2025\2025讯飞系列\复杂图文的逻辑推理挑战赛\图像数据集\image"
OUTPUT_CSV = r"output.csv"

API_KEY = "sk-iBuVfdtBDgb27dhAE25f548fD77a47B086D94dFdBc8a775c"
URL     = "http://maas-api.cn-huabei-1.xf-yun.com/v1/chat/completions"   # ← HTTP
MODEL   = "xqwen2d5s32bvl"                                             # ← 官方 ID
# =====================================

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type":  "application/json"
}

def image_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def call_qwen(question: str, image_b64: str, max_retry: int = 3) -> str:
    full_prompt = (
        "仅根据图片中的信息回答问题，不要输出任何与图片无关的内容。\n"
        f"问题：{question}"
    )
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": full_prompt},
                    {"type": "image_url", "image_url": {"url": image_b64}}
                ]
            }
        ],
        "max_tokens": 512,
        "temperature": 0.2,
        "stream": False
    }

    for attempt in range(max_retry):
        try:
            r = requests.post(URL, headers=HEADERS, json=payload, timeout=60)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"⚠️ 第{attempt+1}次调用失败：{e}")
            time.sleep(2)
    return ""

# ---------------- 主程序 ----------------
def main():
    with open(TEST_CSV, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = [{k.strip(): v.strip() for k, v in row.items()} for row in reader]
    total = len(rows)
    print(f"共 {total} 条待预测数据")

    results = []
    for idx, row in enumerate(rows, 1):
        _id      = row["id"]
        img_rel  = row["image"]
        question = row["question"]

        img_path = os.path.join(IMAGE_DIR, os.path.basename(img_rel))
        if not os.path.isfile(img_path):
            print(f"❌ 图片不存在：{img_path}")
            results.append({"id": _id, "answer": ""})
            continue

        img_b64 = image_to_base64(img_path)
        answer  = call_qwen(question, img_b64)
        results.append({"id": _id, "answer": answer})
        print(f"[{idx:>3}/{total}] id={_id} 完成")
        time.sleep(1)

    with open(OUTPUT_CSV, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "answer"])
        writer.writeheader()
        writer.writerows(results)
    print("✅ 全部完成，结果已保存至", OUTPUT_CSV)

if __name__ == "__main__":
    main()