import argparse
import json
import re
import shutil
from pathlib import Path

from . import assemble, script as scriptmod, video


def main():
    p = argparse.ArgumentParser(description="Gemini + Veo 短影音/短劇生成器")
    p.add_argument("topic", help="主題或一句話劇情")
    p.add_argument("--genre", default="懸疑反轉短劇", help="例：搞笑、暖心、懸疑反轉、知識科普、都市愛情")
    p.add_argument("--lang", default="繁體中文")
    p.add_argument("--scenes", type=int, default=4, help="分鏡數，每個約 8 秒")
    p.add_argument("--aspect", choices=["9:16", "16:9"], default="9:16")
    p.add_argument("--font", help="字幕字型檔路徑（中文需指定，例如 NotoSansCJK）")
    p.add_argument("--script-only", action="store_true", help="只產生劇本，先審稿再花錢生成影片")
    p.add_argument("--dry-run", action="store_true", help="不呼叫 API，測試流程")
    a = p.parse_args()

    slug = re.sub(r"\W+", "_", a.topic)[:30] or "video"
    work = Path("output") / slug
    work.mkdir(parents=True, exist_ok=True)
    spath = work / "script.json"

    if spath.exists():
        data = json.loads(spath.read_text())
    else:
        data = scriptmod.demo_script(a.topic, a.scenes) if a.dry_run else scriptmod.write_script(
            a.topic, a.genre, a.lang, a.scenes)
        spath.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"劇本：{spath}\n標題：{data['title']}")
    if a.script_only:
        return

    if a.dry_run:
        clips = []
        for i, s in enumerate(data["scenes"], 1):
            c = work / f"clip_{i:02d}.mp4"
            if not c.exists():
                assemble._run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=s=720x1280:d=2",
                               "-f", "lavfi", "-i", "anullsrc", "-t", "2", "-shortest", str(c)])
            clips.append(c)
    else:
        clips = video.generate_all(data, work, a.aspect)

    final = work / "final.mp4"
    assemble.assemble(clips, [s["caption"] for s in data["scenes"]], final, a.aspect, a.font)
    (work / "publish.txt").write_text(
        f"{data['title']}\n\n{data['description']}\n\n{' '.join(data['hashtags'])}\n")
    print(f"完成：{final}\n發布文案：{work / 'publish.txt'}")


if __name__ == "__main__":
    main()
