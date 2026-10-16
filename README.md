# ai-video

用 Gemini（寫劇本）+ Veo（生成影片）+ ffmpeg（合成）自動產出短影音/短劇。

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...            # https://aistudio.google.com/apikey

python -m aivideo.cli "外送員發現客人是失散多年的哥哥" --scenes 4 --script-only   # 先審劇本
python -m aivideo.cli "外送員發現客人是失散多年的哥哥" --scenes 4 --font /path/to/NotoSansCJK-Bold.ttc
python -m aivideo.cli "測試" --dry-run                                            # 不花錢測流程
```

輸出在 `output/<主題>/`：`script.json`、`clip_XX.mp4`、`final.mp4`、`publish.txt`（標題/描述/標籤）。
已生成的片段會被重用，中斷後重跑不會重複計費。模型可用 `GEMINI_VIDEO_MODEL` / `GEMINI_TEXT_MODEL` 覆寫。

## 用 Gemini Pro 訂閱額度（不需 API 金鑰）
```bash
python -m aivideo.cli x --workdir examples/ep01 --manual     # 產生 prompts.md，列出缺的片段
# 把 prompts.md 每段貼進 Gemini App / Flow 生成（直式 9:16），下載存成 clip_01.mp4 … 放進該資料夾
python -m aivideo.cli x --workdir examples/ep01 --manual --font /path/to/NotoSansCJK-Bold.ttc   # 片段齊全後合成
```
訂閱額度只算在 Gemini App / Flow，API 金鑰另外計費。

## 漲粉建議
- 每支 20–40 秒、直式 9:16，前 1 秒要有鉤子，結尾留反轉/提問。
- 固定一個系列（同角色、同類型）每天發，比單支爆款更能累積粉絲。
- 同一支影片同時發 TikTok、Reels、Shorts；標題與標籤用 `publish.txt`。
- 平台要求標示 AI 生成內容，請依各平台規定勾選。
