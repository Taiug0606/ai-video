import argparse
import json
import os
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
    p.add_argument("--manual", action="store_true", help="不呼叫任何 API：產生 prompts.md，自己用 Gemini App/Flow 生成片段，放進資料夾後再合成")
    p.add_argument("--workdir", help="直接指定工作資料夾（內含 script.json），例如 examples/ep01")
    p.add_argument("--yes", action="store_true", help="跳過花費確認（排程自動跑時才用）")
    p.add_argument("--dry-run", action="store_true", help="不呼叫 API，測試流程")
    a = p.parse_args()

    slug = re.sub(r"\W+", "_", a.topic)[:30] or "video"
    work = Path(a.workdir) if a.workdir else Path("output") / slug
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

    if a.manual:
        lines = [f"# {data['title']}\n", "每段貼進 Gemini App / Flow 的影片生成（9:16），下載後依序命名放進本資料夾。\n"]
        missing = []
        for i, sc in enumerate(data["scenes"], 1):
            name = f"clip_{i:02d}.mp4"
            if not (work / name).exists():
                missing.append(name)
            lines.append(f"## {name}\n\n{data['character_bible']}\n\n{sc['video_prompt']}\n")
        (work / "prompts.md").write_text("\n".join(lines))
        if missing:
            print(f"提示詞：{work / 'prompts.md'}\n還缺片段：{', '.join(missing)}（放進 {work} 後重跑同一指令即合成）")
            return

    if a.manual:
        clips = [work / f"clip_{i:02d}.mp4" for i in range(1, len(data["scenes"]) + 1)]
    elif a.dry_run:
        clips = []
        for i, s in enumerate(data["scenes"], 1):
            c = work / f"clip_{i:02d}.mp4"
            if not c.exists():
                assemble._run(["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=s=720x1280:d=2",
                               "-f", "lavfi", "-i", "anullsrc", "-t", "2", "-shortest", str(c)])
            clips.append(c)
    else:
        todo = [i for i in range(1, len(data["scenes"]) + 1) if not (work / f"clip_{i:02d}.mp4").exists()]
        secs = len(todo) * 8
        price = os.environ.get("VEO_PRICE_PER_SEC")  # 美元/秒，請依官方最新定價自行設定
        cost = f"約 US${secs * float(price):.2f}" if price else "（未設定 VEO_PRICE_PER_SEC，無法估價）"
        print(f"即將用 Veo 生成 {len(todo)} 個片段 ≈ {secs} 秒，預估花費 {cost}")
        if todo and not a.yes and input("確認開始？輸入 y 繼續：").strip().lower() != "y":
            raise SystemExit("已取消，未產生費用。")
        clips = video.generate_all(data, work, a.aspect)

    final = work / "final.mp4"
    assemble.assemble(clips, [s["caption"] for s in data["scenes"]], final, a.aspect, a.font)
    (work / "publish.txt").write_text(
        f"{data['title']}\n\n{data['description']}\n\n{' '.join(data['hashtags'])}\n")
    print(f"完成：{final}\n發布文案：{work / 'publish.txt'}")


if __name__ == "__main__":
    main()
