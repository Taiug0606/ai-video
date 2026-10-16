"""用 ffmpeg 合成：統一規格、燒入字幕、串接。"""
import subprocess
from pathlib import Path

SIZES = {"9:16": (1080, 1920), "16:9": (1920, 1080)}


def _esc(t: str) -> str:
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def _run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def assemble(clips: list[Path], captions: list[str], out: Path, aspect: str, font: str | None) -> None:
    w, h = SIZES[aspect]
    parts = []
    for i, (clip, cap) in enumerate(zip(clips, captions)):
        part = clip.with_suffix(".norm.mp4")
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30"
        if cap:
            ff = f":fontfile={font}" if font else ""
            vf += (f",drawtext=text='{_esc(cap)}'{ff}:fontsize=64:fontcolor=white:borderw=5:bordercolor=black"
                   f":x=(w-text_w)/2:y=h*0.78")
        _run(["ffmpeg", "-y", "-i", str(clip), "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "20",
              "-c:a", "aac", "-ar", "44100", "-ac", "2", str(part)])
        parts.append(part)
    lst = out.parent / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
