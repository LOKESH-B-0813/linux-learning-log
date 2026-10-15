#!/usr/bin/env python3
"""LinuxLab: a complete beginner-to-expert Linux course that runs REAL commands.
Each module teaches first, then gives checked tasks. Progress is pushed to your GitHub.
Usage: python3 learn.py [--list] [--reset] [--no-git] [--selftest]"""
import datetime as dt, json, os, shutil, subprocess, sys, tempfile
from lessons import LESSONS, MODULES

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("LINUXLAB_REPO", HERE)
WS = os.path.expanduser("~/linuxlab-workspace")
PROG = os.path.join(REPO, "progress.json")
BY_ID = {l["id"]: l for l in LESSONS}
ORDER = [(mi, m, BY_ID[i]) for mi, m in enumerate(MODULES) for i in m["ids"]]
B, G, Y, X = "\033[1m", "\033[32m", "\033[33m", "\033[0m"


def sh(script, cwd, lab, env=None, timeout=15):
    e = dict(os.environ, LAB=lab, **(env or {}))
    try:
        p = subprocess.run(["bash", "-c", script], cwd=cwd, env=e, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)[-4000:]
    except subprocess.TimeoutExpired:
        return 124, f"(stopped after {timeout}s: interactive or endless commands are not supported here)\n"


def execute(line, cwd, lab):
    cf = os.path.join(tempfile.gettempdir(), "linuxlab_cwd")
    if os.path.exists(cf): os.remove(cf)
    rc, out = sh(f'{line}\n__rc=$?\npwd > "{cf}"\nexit $__rc', cwd, lab)
    if os.path.exists(cf): cwd = open(cf).read().strip() or cwd
    return rc, out, cwd


def lab_dir(l): return os.path.join(WS, l["id"])


def setup(l):
    lab = lab_dir(l); shutil.rmtree(lab, ignore_errors=True); os.makedirs(lab)
    sh((BY_ID[l["same_as"]] if l.get("same_as") else l)["setup"], lab, lab)
    return lab


def cleanup(l):
    if l.get("cleanup") and os.path.isdir(lab_dir(l)): sh(l["cleanup"], lab_dir(l), lab_dir(l))


def check(l, lab, cmd, out, cwd, rc):
    return sh(l["check"], lab, lab, env={"LAST_CMD": cmd, "LAST_OUT": out, "CWD": cwd, "LAST_RC": str(rc)})[0] == 0


def load():
    try: return json.load(open(PROG))
    except Exception: return {"done": {}}


def save(prog):
    json.dump(prog, open(PROG, "w"), indent=2)
    rows = ["# My Linux learning log", "",
            f"Completed **{len(prog['done'])} of {len(ORDER)}** hands-on tasks, each auto-checked on a real Linux shell.",
            "", "| # | Module | Task | Date | Command used |", "|---|---|---|---|---|"]
    for n, (mi, m, l) in enumerate(ORDER, 1):
        d = prog["done"].get(l["id"])
        if d:
            c = d["commands"][-1].replace("|", "\\|").replace("`", "'")
            rows.append(f"| {n} | {m['title']} | {l['title']} | {d['date']} | `{c}` |")
    open(os.path.join(REPO, "PROGRESS.md"), "w").write("\n".join(rows) + "\n")


def git_sync(msg):
    def g(*a): return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, timeout=60)
    try:
        if not os.path.isdir(os.path.join(REPO, ".git")): return print("  (not a git repo yet; progress saved locally)")
        g("add", "progress.json", "PROGRESS.md")
        c = g("commit", "-m", msg)
        if c.returncode and "nothing to commit" not in c.stdout: return print("  git commit failed:", (c.stderr or c.stdout).strip()[:200])
        p = g("push")
        print(f"  {G}✓ pushed to GitHub{X}" if p.returncode == 0 else f"  {Y}push failed: {p.stderr.strip()[:160]}{X}")
    except Exception as e:
        print("  git step skipped:", e)


def short(p): return p.replace(os.path.expanduser("~"), "~")


def teach(mi, m):
    print(f"\n{B}══ Module {mi + 1}/{len(MODULES)} · {m['level']} · {m['title']} ══{X}\n{m['teach']}\n{Y}(type :learn any time to read this again){X}")


def play(n, mi, m, l, prog, use_git, shown):
    if mi not in shown: shown.add(mi); teach(mi, m)
    lab = setup(l); cwd = lab; used = []
    def show():
        print(f"\n{B}Task {n}/{len(ORDER)} · {l['title']}{X}\n{l['task']}")
        print(f"{Y}Folder: {short(lab)}   :hint :answer :learn :skip :list :reset :quit{X}\n")
    show()
    while True:
        try: line = input(f"{G}{short(cwd)}{X} $ ").strip()
        except (EOFError, KeyboardInterrupt): print(); cleanup(l); return "quit"
        if not line: continue
        if line in (":quit", ":q", "exit", "quit"): cleanup(l); return "quit"
        if line == ":skip": cleanup(l); return "skip"
        if line == ":hint": print(f"{Y}Hint: {l['hint'] or 'Re-read the module text with :learn'}{X}"); continue
        if line == ":answer": print(f"{Y}One solution:\n{l['answer']}{X}"); continue
        if line == ":learn": teach(mi, m); continue
        if line == ":reset": lab = setup(l); cwd = lab; show(); continue
        if line == ":list":
            for i, (k, mm, x) in enumerate(ORDER, 1): print(f" {G+'✓'+X if x['id'] in prog['done'] else ' '} {i:2}. [{mm['title']}] {x['title']}")
            continue
        if not os.path.isdir(cwd): cwd = lab
        used.append(line); out = ""; rc = 0
        if line.split()[0] == "edit": subprocess.call([os.environ.get("EDITOR", "nano")] + line.split()[1:], cwd=cwd)
        else:
            rc, out, cwd = execute(line, cwd, lab)
            if out: print(out, end="" if out.endswith("\n") else "\n")
        if check(l, lab, line, out, cwd, rc):
            prog["done"][l["id"]] = {"date": dt.date.today().isoformat(), "commands": used[-8:]}
            save(prog); cleanup(l)
            print(f"\n{G}{B}✓ Task {n} passed!{X}")
            left = [x for x in m["ids"] if x not in prog["done"]]
            if not left: print(f"{G}{B}★ Module complete: {m['title']}{X}")
            if use_git: git_sync(f"Complete task {n}: {l['title']}")
            return "done"


def selftest():
    bad = 0
    for l in LESSONS:
        if l.get("selftest") is False: print("SKIP", l["id"]); continue
        lab = setup(l)
        pre = check(l, lab, "", "", lab, 0)
        rc, out, cwd = execute(l["answer"], lab, lab)
        post = check(l, lab, l["answer"], out, cwd, rc)
        ok = post and not pre; bad += not ok; cleanup(l)
        print(("PASS " if ok else "FAIL ") + l["id"] + (" (passes before solving)" if pre else "") + ("" if post else " (answer rejected)"))
    return 1 if bad else 0


def main():
    a = sys.argv[1:]
    if "--selftest" in a: sys.exit(selftest())
    prog = load()
    if "--list" in a:
        for i, (k, m, l) in enumerate(ORDER, 1): print(f"{'✓' if l['id'] in prog['done'] else ' '} {i:2}. [{m['level']}] {m['title']}: {l['title']}")
        return
    if "--reset" in a: prog = {"done": {}}; save(prog); print("Progress reset.")
    if not os.path.exists("/.dockerenv"):
        print(f"{Y}Heads-up: commands you type run for real on THIS machine. Use a VM, WSL or the Docker image if you are unsure.{X}")
        if input("Continue? [y/N] ").strip().lower() != "y": return
    shown = set()
    for n, (mi, m, l) in enumerate(ORDER, 1):
        if l["id"] in prog["done"]: continue
        if play(n, mi, m, l, prog, "--no-git" not in a, shown) == "quit": return
    print(f"\n{G}{B}You finished the whole course! Check PROGRESS.md on your GitHub.{X}")


if __name__ == "__main__":
    main()
