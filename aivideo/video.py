"""用 Veo 生成每個分鏡的影片片段。"""
import time
from pathlib import Path

from google import genai
from google.genai import types

from . import config


def generate_clip(client, prompt: str, out: Path, aspect: str) -> None:
    op = client.models.generate_videos(
        model=config.VIDEO_MODEL,
        prompt=prompt,
        config=types.GenerateVideosConfig(aspect_ratio=aspect, number_of_videos=1),
    )
    while not op.done:
        time.sleep(config.POLL_SECONDS)
        op = client.operations.get(op)
    if op.error or not op.response or not op.response.generated_videos:
        raise RuntimeError(f"Veo 生成失敗: {op.error or '被安全過濾或無結果'}")
    video = op.response.generated_videos[0]
    client.files.download(file=video.video)
    video.video.save(str(out))


def generate_all(script: dict, workdir: Path, aspect: str) -> list[Path]:
    client = genai.Client(api_key=config.api_key())
    clips = []
    for i, scene in enumerate(script["scenes"], 1):
        out = workdir / f"clip_{i:02d}.mp4"
        if not out.exists():  # 斷點續跑，省錢
            prompt = f"{script['character_bible']}\n\n{scene['video_prompt']}"
            print(f"[{i}/{len(script['scenes'])}] 生成中…")
            generate_clip(client, prompt, out, aspect)
        clips.append(out)
    return clips
