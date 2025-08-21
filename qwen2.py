# retry_blank.py
import base64
import csv
import os
import time
import requests

# ========== 与主脚本完全一致 ==========
TEST_CSV   = r"D:\Desktop\作品\2025\2025讯飞系列\复杂图文的逻辑推理挑战赛\test.csv"
IMAGE_DIR  = r"D:\Desktop\作品\2025\2025讯飞系列\复杂图文的逻辑推理挑战赛\图像数据集\image"
OUTPUT_CSV = r"output.csv"

API_KEY = "sk-iBuVfdtBDgb27dhAE25f548fD77a47B086D94dFdBc8a775c"
URL     = "http://maas-api.cn-huabei-1.xf-yun.com/v1/chat/completions"
MODEL   = "xqwen2d5s32bvl"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def image_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def call_qwen(question: str, image_b64: str, max_retry: int = 5) -> str:
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
            time.sleep(3)
    return ""        # 重试完仍失败就留空

# ---------------- 主逻辑 ----------------
def main():
    # 1. 加载 test.csv 生成 id -> (question, image)
    test_map = {}
    with open(TEST_CSV, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            _id = row["id"].strip()
            test_map[_id] = (row["question"].strip(), row["image"].strip())

    # 2. 读取 output.csv，把需要补漏的行挑出来
    rows_out = []
    need_fix = []
    with open(OUTPUT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_out.append(row)
            if not row["answer"].strip():          # 空值
                need_fix.append(row["id"].strip())

    if not need_fix:
        print("所有答案均已生成，无需补漏。")
        return

    print(f"发现 {len(need_fix)} 条空答案，开始补漏...")
    for idx, _id in enumerate(need_fix, 1):
        if _id not in test_map:
            print(f"❌ test.csv 中找不到 id={_id}，跳过")
            continue
        question, img_rel = test_map[_id]
        img_path = os.path.join(IMAGE_DIR, os.path.basename(img_rel))
        if not os.path.isfile(img_path):
            print(f"❌ 图片不存在：{img_path}，跳过")
            continue

        img_b64 = image_to_base64(img_path)
        answer  = call_qwen(question, img_b64)

        # 写回内存
        for r in rows_out:
            if r["id"] == _id:
                r["answer"] = answer
                break
        print(f"[{idx:>2}/{len(need_fix)}] id={_id} 补漏完成")
        time.sleep(1)

    # 3. 覆盖写回 output.csv
    with open(OUTPUT_CSV, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "answer"])
        writer.writeheader()
        writer.writerows(rows_out)
    print("✅ 补漏完成，已覆盖保存至", OUTPUT_CSV)

if __name__ == "__main__":
    main()