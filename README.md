# 2025 iFLYTEK 复杂图文逻辑推理挑战赛

## Qwen 系列一站式解决方案

### 1. 项目结构

```
├─ qwen.py            # 主脚本：一次性调用 Qwen2.5-VL-32B-Instruct 推理 484 条
├─ retry_blank.py     # 补漏脚本：只针对空 answer 重新请求 Qwen
├─ fix.py             # 编码修复：强制 UTF-8 无 BOM，解决平台提交编码报错
├─ test.csv           # 官方测试集（id,image,question）
└─ image/             # 484 张 png 原图
其他的都是无关文件可以不看
```

### 2. 环境要求

- **Python** ≥ 3.10
- **依赖包安装**：
  ```bash
  pip install requests chardet
  ```

### 3. 配置说明（四行即可跑通）

```python
API_KEY = "sk-iBuVfdtBDgb27dhAE25f548fD77a47B086D94dFdBc8a775c"
URL = "http://maas-api.cn-huabei-1.xf-yun.com/v1/chat/completions"
MODEL = "xqwen2d5s32bvl"                # 官方模型 ID
IMAGE_DIR = "D:...\image"              # 你的图片文件夹路径
```

### 4. 运行流程

#### Step-1: 首次批量推理
```bash
python qwen.py
```
→ 生成 `output.csv`（默认 GBK 或带 BOM，可能提交失败）

#### Step-2: 编码修复（必做）
```bash
python fix.py
```
→ 原地覆盖为 UTF-8 无 BOM

#### Step-3: 补漏空答案（可选）
```bash
python retry_blank.py
```
→ 只针对 answer 为空的 id 重新调用 Qwen，再写回 `output.csv`

### 5. 脚本功能速览

#### `qwen.py`
- 逐行读取 `test.csv` → 图片转 base64 → 调用 Qwen → 写 `output.csv`
- 已内置重试 3 次、sleep 1s、失败置空
- 实验发现部分图片响应缓慢，应该延长

#### `retry_blank.py`
- 读取 `output.csv`，找出空 answer 对应的 id
- 回查 `test.csv` 获取 question+image → 再次调用 Qwen → 覆盖写入

#### `fix.py`
- 自动检测源编码（GBK/GB2312/UTF-8-BOM）→ 强制 UTF-8 无 BOM
- 出现 PermissionError 时提示"请先关闭 Excel/VSCode"

### 6. 常见问题（Qwen 视角）

| 问题类型 | 解决方案 |
|---------|----------|
| **403/500 错误** | 检查 MODEL、URL、API_KEY；降低 QPS；确认网络未走代理 |
| **UnicodeDecodeError** | 运行 `fix.py`，一键转码 |
| **PermissionError** | 关闭所有占用 `output.csv` 的程序后再 fix |

---

> **注意**：请确保按照上述流程依次执行，特别是编码修复步骤，这是成功提交的关键。
