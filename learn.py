#!/usr/bin/env python3
"""LinuxLab: type REAL Linux commands, get auto-checked, and push progress to GitHub.
Usage: python3 learn.py [--list] [--reset] [--no-git] [--selftest]"""
import datetime as dt, json, os, shutil, subprocess, sys, tempfile
from lessons import LESSONS

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("LINUXLAB_REPO", HERE)          # folder that is your git repo
WS = os.path.expanduser("~/linuxlab-workspace")        # where practice files live
PROG = os.path.join(REPO, "progress.json")
BY_ID = {l["id"]: l for l in LESSONS}
B, G, Y, R, X = "\033[1m", "\033[32m", "\033[33m", "\033[31m", "\033[0m"


def sh(script, cwd, lab, env=None, timeout=15):
    e = dict(os.environ, LAB=lab, **(env or {}))
    try:
        p = subprocess.run(["bash", "-c", script], cwd=cwd, env=e, capture_output=True,
                           text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)[-4000:]
    except subprocess.TimeoutExpired:
        return 124, f"(stopped after {timeout}s: interactive or endless commands are not supported here)\n"


def lab_dir(l): return os.path.join(WS, l["id"])


def setup(l):
    lab = lab_dir(l)
    shutil.rmtree(lab, ignore_errors=True)
    os.makedirs(lab)
    src = BY_ID[l["same_as"]] if l.get("same_as") else l
    sh(src["setup"], lab, lab)
    return lab


def cleanup(l):
    if l.get("cleanup") and os.path.isdir(lab_dir(l)):
        sh(l["cleanup"], lab_dir(l), lab_dir(l))


def load():
    try:
        return json.load(open(PROG))
    except Exception:
        return {"done": {}}


def save(prog):
    json.dump(prog, open(PROG, "w"), indent=2)
    rows = ["# My Linux learning log", "",
            f"Completed **{len(prog['done'])} of {len(LESSONS)}** hands-on lessons, each auto-checked on a real Linux shell.",
            "", "| # | Lesson | Level | Date | Command used |", "|---|---|---|---|---|"]
    for i, l in enumerate(LESSONS, 1):
        d = prog["done"].get(l["id"])
        if d:
            c = d["commands"][-1].replace("|", "\\|").replace("`", "'")
            rows.append(f"| {i} | {l['title']} | {l['level']} | {d['date']} | `{c}` |")
    open(os.path.join(REPO, "PROGRESS.md"), "w").write("\n".join(rows) + "\n")


def git_sync(msg):
    def g(*a): return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, timeout=60)
    try:
        if not os.path.isdir(os.path.join(REPO, ".git")):
            return print("  (this folder is not a git repo yet; progress saved locally)")
        g("add", "progress.json", "PROGRESS.md")
        c = g("commit", "-m", msg)
        if c.returncode and "nothing to commit" not in c.stdout:
            return print("  git commit failed:", (c.stderr or c.stdout).strip()[:200])
        p = g("push")
        print(f"  {G}✓ pushed to GitHub{X}" if p.returncode == 0 else
              f"  {Y}push failed (see README, GitHub login): {p.stderr.strip()[:160]}{X}")
    except Exception as e:
        print("  git step skipped:", e)


def short(p): return p.replace(os.path.expanduser("~"), "~")


def show(n, l, lab):
    print(f"\n{B}Lesson {n}/{len(LESSONS)}  [{l['level']}]  {l['title']}{X}\n{l['task']}")
    print(f"{Y}Folder: {short(lab)}   Commands: :hint :answer :skip :list :reset :quit{X}\n")


def play(n, l, prog, use_git):
    lab = setup(l); cwd = lab; used = []
    cwdfile = os.path.join(tempfile.gettempdir(), "linuxlab_cwd")
    show(n, l, lab)
    while True:
        try:
            line = input(f"{G}{short(cwd)}{X} $ ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); cleanup(l); return "quit"
        if not line: continue
        if line in (":quit", ":q", "exit", "quit"): cleanup(l); return "quit"
        if line == ":skip": cleanup(l); return "skip"
        if line == ":hint": print(f"{Y}Hint: {l['hint']}{X}"); continue
        if line == ":answer": print(f"{Y}One solution:\n{l['answer']}{X}"); continue
        if line == ":reset": lab = setup(l); cwd = lab; show(n, l, lab); continue
        if line == ":list":
            for i, x in enumerate(LESSONS, 1): print(f" {G+'✓'+X if x['id'] in prog['done'] else ' '} {i:2}. {x['title']}")
            continue
        if not os.path.isdir(cwd): cwd = lab
        used.append(line); out = ""
        if line.split()[0] == "edit":
            subprocess.call([os.environ.get("EDITOR", "nano")] + line.split()[1:], cwd=cwd)
        else:
            if os.path.exists(cwdfile): os.remove(cwdfile)
            _, out = sh(f'{line}\n__rc=$?\npwd > "{cwdfile}"\nexit $__rc', cwd, lab)
            if out: print(out, end="" if out.endswith("\n") else "\n")
            if os.path.exists(cwdfile): cwd = open(cwdfile).read().strip() or cwd
        rc, _ = sh(l["check"], lab, lab, env={"LAST_CMD": line, "LAST_OUT": out, "CWD": cwd})
        if rc == 0:
            prog["done"][l["id"]] = {"date": dt.date.today().isoformat(), "commands": used[-8:]}
            save(prog); cleanup(l)
            print(f"\n{G}{B}✓ Lesson {n} passed!{X}  {l['why']}")
            if use_git: git_sync(f"Complete lesson {n}: {l['title']}")
            return "done"


def selftest():
    bad = 0
    for l in LESSONS:
        lab = setup(l)
        env = {"LAST_CMD": "", "LAST_OUT": "", "CWD": lab}
        pre = sh(l["check"], lab, lab, env=env)[0] == 0
        _, out = sh(l["answer"], lab, lab)
        post = sh(l["check"], lab, lab, env={"LAST_CMD": l["answer"], "LAST_OUT": out, "CWD": lab})[0] == 0
        ok = post and not pre
        bad += not ok; cleanup(l)
        print(("PASS " if ok else "FAIL ") + l["id"] + (" (already passes before solving)" if pre else "") + ("" if post else " (answer rejected)"))
    return 1 if bad else 0


def main():
    a = sys.argv[1:]
    if "--selftest" in a: sys.exit(selftest())
    prog = load()
    if "--list" in a:
        for i, l in enumerate(LESSONS, 1): print(f"{'✓' if l['id'] in prog['done'] else ' '} {i:2}. [{l['level']}] {l['title']}")
        return
    if "--reset" in a: prog = {"done": {}}; save(prog); print("Progress reset.")
    if not os.path.exists("/.dockerenv"):
        print(f"{Y}Heads-up: commands you type run for real on THIS machine. Use a VM, WSL or the Docker image if you are unsure.{X}")
        if input("Continue? [y/N] ").strip().lower() != "y": return
    for n, l in enumerate(LESSONS, 1):
        if l["id"] in prog["done"]: continue
        if play(n, l, prog, "--no-git" not in a) == "quit": return
    print(f"\n{G}{B}All lessons complete! Check your GitHub profile for PROGRESS.md.{X}")


if __name__ == "__main__":
    main()
