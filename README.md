# LinuxLab

Practise **real Linux commands** (not a simulation). Each lesson gives you a task, you type commands, and the tool checks the result on your real system. When you pass, it moves to the next lesson and **commits and pushes your progress to your GitHub repo** (`PROGRESS.md` shows on your profile as proof of practice).

**A complete course, zero to expert, with no outside websites needed.** 15 modules and 50 checked tasks. Every module first TEACHES the topic in plain words, then gives small tasks that get harder:

- **Beginner:** moving around, files and folders, reading and writing text, finding things, getting help
- **Intermediate:** permissions, users, processes, pipes and text tools, packages and services
- **Advanced:** networking, Bash scripting, backups and cron, disk/memory/logs, SSH security and git

## Setup (about 10 minutes)

**You need a real Linux shell:** Ubuntu on WSL (Windows), a VirtualBox Ubuntu VM, or any Linux machine.

1. Create an empty public repo on GitHub, for example `linux-learning-log`.
2. In your Linux terminal:
   ```bash
   sudo apt update && sudo apt install -y git python3 curl nano gh
   gh auth login                      # choose GitHub.com, HTTPS, login with browser
   git config --global user.name  "Your Name"
   git config --global user.email "you@example.com"
   git clone https://github.com/YOUR-USER/linux-learning-log.git
   cd linux-learning-log
   ```
3. Copy these project files into that folder (`learn.py`, `lessons.py`, `Dockerfile`, `README.md`, `INTERVIEW_QUESTIONS.md`), then:
   ```bash
   git add . && git commit -m "Add LinuxLab" && git push
   python3 learn.py
   ```

## How it works

- Type normal shell commands at the prompt. `cd` works, and commands run for real in a practice folder (`~/linuxlab-workspace`).
- The lesson is checked after every command. Pass = next lesson + automatic `git commit` and `git push`.
- Special commands: `:learn` (re-read the module), `:hint`, `:answer`, `:skip`, `:list`, `:reset`, `:quit`. Use `edit file` to open nano.
- Not supported: interactive programs (vim, top) and variables that persist between commands.
- Try without answers first. Struggling is where the learning happens.

## Safer option: Docker sandbox

If you are nervous about typing real commands:
```bash
docker build -t linuxlab .
docker run -it --rm -v "$PWD":/home/learner/linuxlab linuxlab
```
Progress is saved to the mounted folder. Push from your normal terminal afterwards:
`git add -A && git commit -m "progress" && git push`

## Add your own lessons

Open `lessons.py`, copy any `L(...)` block, and edit: `task`, `setup` (script that prepares files), `check` (script, exit 0 = pass; can use `$LAST_CMD` and `$LAST_OUT`), and `answer`. Then verify with:
```bash
python3 learn.py --selftest
```

## Troubleshooting

- **Push failed:** run `gh auth status`; if logged out, run `gh auth login`. Progress is still saved locally, so push manually.
- **Commit failed:** set `git config --global user.name/email` (step 2).
- **Start over:** `python3 learn.py --reset`
