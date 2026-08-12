#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""安全重推：base64 仅在进程内计算，绝不进命令行参数；已存在文件带 sha 做覆盖更新。"""
import os, sys, json, base64, subprocess, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = "ddyuan-spec/taixiaohu"
BRANCH = "main"
PREFIX = "睡眠任务闭环一期"

def gh(*args, input_file=None):
    cmd = ["gh", "api", *args]
    if input_file:
        cmd += ["--input", input_file]
    env = dict(os.environ)
    env["HTTPS_PROXY"] = ""
    return subprocess.run(cmd, capture_output=True, text=True, env=env)

def main():
    files = []
    for dirpath, _, fnames in os.walk(ROOT):
        for fn in fnames:
            if fn == "body.json" or fn == "push_fix.py" or fn == "gen_gallery.py":
                # gen_gallery.py 也重推一次，保持一致
                pass
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            files.append(rel)
    files = sorted(files)
    ok = 0; fail = 0
    for rel in files:
        enc = urllib.parse.quote(f"{PREFIX}/{rel}", safe="/")
        url = f"repos/{REPO}/contents/{enc}"
        data = open(os.path.join(ROOT, rel), "rb").read()
        b64 = base64.b64encode(data).decode("ascii")
        # 取已存在 sha（用于覆盖更新）；不存在则不带
        sha = None
        r = gh(f"repos/{REPO}/contents/{enc}")
        if r.returncode == 0:
            try:
                sha = json.loads(r.stdout).get("sha")
            except Exception:
                sha = None
        body = {"message": f"fix: re-upload {PREFIX}/{rel}", "content": b64, "branch": BRANCH}
        if sha:
            body["sha"] = sha
        with open(os.path.join(ROOT, "body.json"), "w", encoding="utf-8") as f:
            json.dump(body, f)
        rr = gh("-X", "PUT", url, input_file="body.json")
        if rr.returncode == 0:
            print(f"OK   {rel}  ({len(data)} bytes)")
            ok += 1
        else:
            print(f"FAIL {rel}\n{rr.stderr[:300]}")
            fail += 1
    if os.path.exists(os.path.join(ROOT, "body.json")):
        os.remove(os.path.join(ROOT, "body.json"))
    print(f"=== 重推完成: ok={ok} fail={fail} ===")

if __name__ == "__main__":
    main()
