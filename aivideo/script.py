"""用 Gemini 把主題寫成適合短影音的分鏡劇本（JSON）。"""
import json

from google import genai
from google.genai import types

from . import config

PROMPT = """你是爆款短影音（TikTok / Reels / YouTube Shorts）編劇。
主題：{topic}
類型：{genre}
語言（旁白/對白/文案）：{lang}
請寫 {scenes} 個分鏡，每個分鏡 8 秒，總長約 {total} 秒。

規則：
- 第 1 個分鏡必須在 1 秒內抓住注意力（鉤子）；最後一個分鏡要有反轉或讓人想留言/追蹤的結尾。
- 劇情緊湊、情緒強、畫面感強；對白簡短。
- "character_bible" 用英文詳細描述主角外觀（臉、髮型、服裝、年齡），確保各分鏡角色一致。
- 每個分鏡的 "video_prompt" 用英文，包含：場景、鏡頭運動、光線、動作、以及引號內的簡短對白或音效；不要出現文字字幕。
- "caption" 是該分鏡的字幕（{lang}，一行，14 字以內）。
- "hashtags" 5-8 個，"title" 25 字內且有點擊慾望。

輸出 JSON：
{{"title": str, "description": str, "hashtags": [str], "character_bible": str,
  "scenes": [{{"video_prompt": str, "caption": str}}]}}
"""


def write_script(topic: str, genre: str, lang: str, scenes: int) -> dict:
    client = genai.Client(api_key=config.api_key())
    resp = client.models.generate_content(
        model=config.TEXT_MODEL,
        contents=PROMPT.format(topic=topic, genre=genre, lang=lang, scenes=scenes, total=scenes * 8),
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return json.loads(resp.text)


def demo_script(topic: str, scenes: int) -> dict:
    """--dry-run 用，不呼叫 API。"""
    return {
        "title": f"【示範】{topic}",
        "description": "dry-run",
        "hashtags": ["#ai", "#shorts"],
        "character_bible": "A young woman, 25, short black hair, red jacket",
        "scenes": [{"video_prompt": f"Scene {i + 1}: {topic}", "caption": f"第 {i + 1} 幕"} for i in range(scenes)],
    }
