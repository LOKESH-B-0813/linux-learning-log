"""Lesson bank. Each lesson = setup script, task text, check script, answer.
The check script runs after EVERY command you type. Exit code 0 = passed.
Env available to scripts: $LAB (lesson folder), $LAST_CMD, $LAST_OUT, $CWD.
To add a lesson: copy any L(...) block below and edit it."""


def L(id, level, title, task, setup, check, answer, hint="", why="", **kw):
    return dict(id=id, level=level, title=title, task=task, setup=setup.strip(),
                check=check.strip(), answer=answer.strip(), hint=hint, why=why, **kw)


T01_SETUP = r'''printf 'name,dept,city\nasha,Engineering,Chennai\nravi,Support,Madurai\nmeena,Engineering,Karur\nkarthik,Engineering,Chennai\nlatha,HR,Salem\nsuresh,Support,Chennai\nanu,Engineering,Coimbatore\n' > employees.csv'''
LOG_SETUP = r'''for i in $(seq 1 20); do ip=10.0.0.$([ $i -le 12 ] && echo 9 || echo $((i%3+1))); st=$([ $((i%5)) -eq 0 ] && echo 500 || echo 200); echo "$ip - - [15/Oct/2026] \"GET /p$i HTTP/1.1\" $st 512"; done > access.log'''

LESSONS = [
L("t01", "Toolkit", "Extract a column",
  "employees.csv has the columns name,dept,city. Save only the dept values (without the header line) into depts.txt.",
  T01_SETUP,
  r'''[ -f depts.txt ] && [ "$(cat depts.txt)" = "$(tail -n +2 employees.csv | cut -d, -f2)" ]''',
  "tail -n +2 employees.csv | cut -d, -f2 > depts.txt",
  "cut -d, -f2 picks field 2 using comma as the delimiter. tail -n +2 skips the header.",
  "Pulling one column out of CSV exports is everyday work in support and operations."),

L("t02", "Toolkit", "Count and rank",
  "Create dept_count.txt that lists each department with how many employees it has, biggest first (Engineering should be on line 1).",
  "", r'''[ -f dept_count.txt ] && head -1 dept_count.txt | grep -Eq '^ *4 +Engineering' ''',
  "cut -d, -f2 employees.csv | tail -n +2 | sort | uniq -c | sort -nr > dept_count.txt",
  "Chain: cut | tail | sort | uniq -c | sort -nr. uniq only merges neighbours, so sort first.",
  "sort | uniq -c | sort -nr is the classic way to find 'top N' in any log or export.", same_as="t01"),

L("t03", "Toolkit", "Edit a config with sed",
  "app.conf has mode=debug. Change it to mode=production inside the file itself, and leave the other lines alone.",
  r'''printf 'port=8080\nmode=debug\nlog_level=info\n' > app.conf''',
  r'''grep -qx 'mode=production' app.conf && grep -qx 'port=8080' app.conf && grep -qx 'log_level=info' app.conf''',
  "sed -i 's/mode=debug/mode=production/' app.conf",
  "sed -i 's/old/new/' file edits the file in place.",
  "Changing config values from a script is how servers are configured at scale."),

L("t04", "Toolkit", "Sum a column with awk",
  "sales.txt has 'item quantity' per line. Write the total of the quantities into total.txt.",
  r'''printf 'apple 10\nbanana 5\napple 7\ncherry 3\n' > sales.txt''',
  r'''[ "$(tr -d '[:space:]' < total.txt 2>/dev/null)" = "25" ]''',
  "awk '{s+=$2} END{print s}' sales.txt > total.txt",
  "awk '{ s+=$2 } END { print s }' adds field 2 of every line.",
  "awk is the fastest way to calculate on columns of text without opening Excel."),

L("t05", "Toolkit", "Compare two files",
  "config_old and config_new differ. Save the differences into changes.diff.",
  r'''printf 'port=80\nmode=debug\n' > config_old; printf 'port=80\nmode=prod\n' > config_new''',
  r'''[ -s changes.diff ] && grep -q '^[<>]' changes.diff''',
  "diff config_old config_new > changes.diff",
  "diff fileA fileB shows lines starting with < (only in A) and > (only in B).",
  "After a change goes wrong, 'what is different from the working version?' is the first question."),

L("t06", "Toolkit", "Make a backup archive",
  "Create a compressed archive project-backup.tar.gz that contains the project folder.",
  r'''mkdir -p project/src; echo 'print(1)' > project/src/app.py; echo notes > project/README.txt''',
  r'''tar -tzf project-backup.tar.gz 2>/dev/null | grep -q 'project/src/app.py' ''',
  "tar -czf project-backup.tar.gz project",
  "tar -czf archive.tar.gz folder  (c=create, z=gzip, f=filename). List with tar -tzf.",
  "Backups and log archives are routine tasks for every system administrator."),

L("t07", "Toolkit", "Symlink a release",
  "releases/ has v1 and v2. Create a symlink named current that points to releases/v2.",
  "mkdir -p releases/v1 releases/v2",
  r'''[ -L current ] && [ "$(readlink current)" = "releases/v2" ]''',
  "ln -s releases/v2 current",
  "ln -s target linkname",
  "Deployments switch versions by moving a 'current' symlink. Rollback takes one command."),

L("r01", "Real-world", "Permission denied",
  "./backup.sh fails with 'Permission denied'. Fix the problem and run the script successfully.",
  r'''printf '#!/bin/bash\necho backup ok\n' > backup.sh; chmod 644 backup.sh''',
  r'''[ -x backup.sh ] && echo "$LAST_OUT" | grep -q 'backup ok' ''',
  "chmod +x backup.sh\n./backup.sh",
  "A script needs the execute bit: chmod +x.",
  "Probably the single most common error new engineers hit."),

L("r02", "Real-world", "Count server errors",
  "access.log is a web server log. How many requests returned status 500? Print the number.",
  LOG_SETUP,
  r'''[ "$(echo "$LAST_OUT" | tr -d '[:space:]')" = "4" ] && echo "$LAST_CMD" | grep -Eq 'grep|awk' ''',
  "grep -c ' 500 ' access.log",
  "grep -c counts matching lines. The status code is surrounded by spaces.",
  "Your manager asks: 'how many errors since the deploy?' This is how you answer."),

L("r03", "Real-world", "Find the noisiest client",
  "Which IP address sent the most requests in access.log? Print that IP with its count (just the top one).",
  "", r'''echo "$LAST_OUT" | grep -q '10\.0\.0\.9' && echo "$LAST_CMD" | grep -Eq 'uniq|awk' && [ "$(echo "$LAST_OUT" | grep -c .)" -le 3 ]''',
  "awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -1",
  "Field 1 is the IP: awk '{print $1}' | sort | uniq -c | sort -nr | head",
  "Spotting a single abusive client or a bot is routine for SOC and cloud support.", same_as="r02"),

L("r04", "Real-world", "Disk is full",
  "var_log/ is eating the disk. Find the biggest file in it and delete only that file.",
  r'''mkdir var_log; head -c 3000000 /dev/zero > var_log/app.log.1; echo ok > var_log/app.log; echo ok > var_log/boot.log''',
  r'''[ ! -e var_log/app.log.1 ] && [ -e var_log/app.log ] && [ -e var_log/boot.log ]''',
  "ls -lS var_log\nrm var_log/app.log.1",
  "ls -lS sorts by size (biggest first). du -ah var_log | sort -rh also works.",
  "'Disk 100%' alerts are among the most frequent real incidents."),

L("r05", "Real-world", "Free the port",
  "A dev server is blocking port 8080. Find the PID that is listening on it and stop that process.",
  r'''pkill -f '[h]ttp.server 8080' 2>/dev/null; nohup python3 -m "http.server" 8080 >/dev/null 2>&1 </dev/null & echo $! > pid; sleep 1''',
  r'''sleep 0.5; p=$(cat pid); ! kill -0 "$p" 2>/dev/null || grep -q 'State:.*Z' /proc/$p/status''',
  "kill $(cat pid)",
  "ss -ltnp | grep 8080 shows the PID. Then kill <PID>. (Try plain kill before kill -9.)",
  "'Address already in use' is a classic deployment failure.",
  cleanup=r'''pkill -f '[h]ttp.server 8080' 2>/dev/null; true'''),

L("r06", "Real-world", "Talk to a web server",
  "A web server is running on port 8081. Use curl to fetch its home page and save the response into response.html.",
  r'''echo 'Hello LinuxLab' > index.html; pkill -f '[h]ttp.server 8081' 2>/dev/null; nohup python3 -m "http.server" 8081 --directory "$LAB" >/dev/null 2>&1 </dev/null & sleep 1''',
  r'''grep -q 'Hello LinuxLab' response.html''',
  "curl -s http://localhost:8081 -o response.html",
  "curl -s URL -o filename   (or: curl -s URL > filename)",
  "curl is the first tool for testing any API or website from a server.",
  cleanup=r'''pkill -f '[h]ttp.server 8081' 2>/dev/null; true'''),

L("r07", "Real-world", "command not found",
  "bin/hello works as ./bin/hello but 'hello' alone says command not found. Run it by the plain name hello, by adding bin to PATH for that one command.",
  r'''mkdir bin; printf '#!/bin/bash\necho hello from bin\n' > bin/hello; chmod +x bin/hello''',
  r'''echo "$LAST_OUT" | grep -q 'hello from bin' && echo "$LAST_CMD" | grep -q 'PATH=' && echo "$LAST_CMD" | grep -Eq '(^| )hello( |$)' ''',
  "PATH=$PATH:$PWD/bin hello",
  "VAR=value command sets a variable for that one command. PATH lists where the shell looks for programs.",
  "Understanding PATH solves a huge share of 'works on my machine' problems."),

L("r08", "Real-world", "Write a loop script",
  "Write report.sh that uses a loop to print 'Hello <name>' for every line in names.txt.",
  r'''printf 'asha\nravi\nmeena\n' > names.txt''',
  r'''[ -f report.sh ] && grep -Eq 'while|for' report.sh && diff <(bash report.sh) <(sed 's/^/Hello /' names.txt) >/dev/null''',
  r'''printf 'while read n; do echo "Hello $n"; done < names.txt\n' > report.sh''',
  "Create the file with: edit report.sh  (opens nano). Idea: while read n; do ...; done < names.txt",
  "Automating repeated work with small scripts is the heart of DevOps."),

L("r09", "Real-world", "Schedule with cron",
  "Put a cron line into crontab.txt that runs /opt/backup.sh every day at 02:30.",
  "touch crontab.txt",
  r'''grep -Eq '^30 +2 +\* +\* +\* +/opt/backup\.sh' crontab.txt''',
  "echo '30 2 * * * /opt/backup.sh' > crontab.txt",
  "Format: minute hour day-of-month month day-of-week command",
  "Backups, cleanups and reports all run from cron or a systemd timer."),

L("r10", "Real-world", "Clean up old logs",
  "Delete .log files older than 30 days in this folder, but keep new.log.",
  r'''touch -d '40 days ago' old1.log old2.log; touch new.log''',
  r'''[ ! -e old1.log ] && [ ! -e old2.log ] && [ -e new.log ]''',
  "find . -name '*.log' -mtime +30 -delete",
  "find . -name '*.log' -mtime +30  (add -delete only after you checked the list!)",
  "Log rotation and cleanup keep servers healthy."),

L("r11", "Real-world", "Fix an SSH key",
  "SSH rejects secret.key with 'UNPROTECTED PRIVATE KEY FILE'. Set permissions so only the owner can read and write it.",
  r'''echo fake-key > secret.key; chmod 644 secret.key''',
  r'''[ "$(stat -c %a secret.key)" = "600" ]''',
  "chmod 600 secret.key",
  "chmod 600 = rw------- (owner only)",
  "You will meet this the first time you SSH into an AWS EC2 instance with a .pem file."),

L("r12", "Real-world", "Hunt the attacker",
  "auth.log is an SSH log. List the IPs behind FAILED password attempts with counts, highest first.",
  r'''for i in $(seq 1 8); do echo "Oct 15 10:0$i:01 srv sshd[10$i]: Failed password for root from 203.0.113.5 port 22 ssh2"; done > auth.log
for i in 1 2 3; do echo "Oct 15 11:0$i:01 srv sshd[20$i]: Failed password for admin from 198.51.100.7 port 22 ssh2"; done >> auth.log
echo "Oct 15 12:00:01 srv sshd[300]: Accepted password for alice from 192.0.2.10 port 22 ssh2" >> auth.log''',
  r'''echo "$LAST_OUT" | head -1 | grep -Eq '8 +203\.0\.113\.5' && echo "$LAST_CMD" | grep -q Failed && ! echo "$LAST_OUT" | grep -q 192.0.2.10''',
  "grep 'Failed password' auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr",
  "grep Failed | awk (IP is 3rd from the end) | sort | uniq -c | sort -nr",
  "This exact task is Level 1 SOC analyst work: brute-force detection."),

L("r13", "Real-world", "Split output and errors",
  "Run ./build.sh so that normal output goes to out.log and error messages go to err.log.",
  r'''printf '#!/bin/bash\necho build ok\necho "warning: low memory" >&2\n' > build.sh; chmod +x build.sh''',
  r'''grep -q 'build ok' out.log && grep -q warning err.log && ! grep -q warning out.log''',
  "./build.sh > out.log 2> err.log",
  "> redirects stdout (stream 1). 2> redirects stderr (stream 2).",
  "Cron jobs and CI pipelines depend on capturing errors separately."),

L("r14", "Real-world", "First git commit",
  "Turn the proj folder into a git repository and make your first commit. (If git asks who you are, set git config --global user.name and user.email.)",
  r'''mkdir proj; echo 'print("hi")' > proj/app.py''',
  r'''git -C proj rev-parse --verify HEAD >/dev/null 2>&1''',
  "git -C proj init -q\ngit -C proj add .\ngit -C proj -c user.name=t -c user.email=t@t.t commit -qm first",
  "cd proj; git init; git add .; git commit -m 'first commit'",
  "Every DevOps and cloud workflow starts from version control."),
]


def N(id, title, task, setup, check, answer, hint="", **kw):
    return L(id, "", title, task, setup, check, answer, hint, "", **kw)


LESSONS += [
N("n01", "Where am I?", "Print the full path of the folder you are in.", "",
  r'''[ "$(echo "$LAST_OUT" | tr -d '[:space:]')" = "$LAB" ] && echo "$LAST_CMD" | grep -q pwd''', "pwd", "pwd means 'print working directory'."),
N("n02", "Walk into folders", "Go into docs/work/reports with ONE cd command.", "mkdir -p docs/work/reports",
  r'''[ "$CWD" = "$LAB/docs/work/reports" ]''', "cd docs/work/reports", "cd takes a path with slashes: cd a/b/c. Tab completes names."),
N("n03", "Find the hidden file", "A hidden file lives in this folder. Show what is written inside it.",
  r'''echo 'treasure: you found me' > .secret; echo visible > readme.txt''',
  r'''echo "$LAST_OUT" | grep -q treasure && echo "$LAST_CMD" | grep -q cat''', "ls -a\ncat .secret", "Hidden files start with a dot. ls -a shows them."),
N("f01", "Build a folder tree", "Create projects/web/css and projects/web/js with a single mkdir command.", "",
  r'''[ -d projects/web/css ] && [ -d projects/web/js ]''', "mkdir -p projects/web/css projects/web/js", "mkdir -p creates missing parent folders; you can list several folders."),
N("f02", "Copy and rename", "Copy a.txt into the backup folder, then rename b.txt to report.txt.",
  r'''mkdir backup; echo a > a.txt; echo b > b.txt''',
  r'''[ -f backup/a.txt ] && [ -f a.txt ] && [ -f report.txt ] && [ ! -e b.txt ]''', "cp a.txt backup/\nmv b.txt report.txt", "cp source destination. mv also renames."),
N("f03", "Delete a folder", "Delete the old folder with everything inside it, but keep the keep folder.",
  r'''mkdir -p old/deep keep; touch old/deep/x.txt keep/y.txt''',
  r'''[ ! -e old ] && [ -f keep/y.txt ]''', "rm -r old", "A folder needs rm -r. Double-check the name first."),
N("x01", "Write and append", "Create todo.txt with two lines, 'learn linux' and 'learn aws', using echo.", "",
  r'''[ "$(cat todo.txt)" = "$(printf 'learn linux\nlearn aws')" ]''', "echo \"learn linux\" > todo.txt\necho \"learn aws\" >> todo.txt", "> overwrites a file, >> adds to the end."),
N("x02", "Read the end of a file", "Show only the last 2 lines of data.txt.", r'''seq 1 10 | sed 's/^/line /' > data.txt''',
  r'''[ "$(echo "$LAST_OUT")" = "$(printf 'line 9\nline 10')" ] && echo "$LAST_CMD" | grep -q tail''', "tail -n 2 data.txt", "tail -n NUMBER file"),
N("s01", "Search text", "Count how many lines in log.txt contain the word error, ignoring upper or lower case.",
  r'''printf 'Error: disk full\ninfo ok\nERROR: db down\nwarn low\nerror: timeout\n' > log.txt''',
  r'''[ "$(echo "$LAST_OUT" | tr -d '[:space:]')" = 3 ] && echo "$LAST_CMD" | grep -q grep''', "grep -ic error log.txt", "-i ignores case, -c counts matching lines."),
N("s02", "Find a buried file", "target.conf is hidden somewhere in this folder tree. Print its path.",
  r'''mkdir -p a/b/c a/d; echo x > a/b/c/target.conf; echo y > a/d/other.txt''',
  r'''echo "$LAST_OUT" | grep -q 'a/b/c/target.conf' && echo "$LAST_CMD" | grep -q find''', "find . -name target.conf", "find where -name filename"),
N("s03", "Count lines", "Save the number of lines in numbers.txt into count.txt.", "seq 1 42 > numbers.txt",
  r'''[ "$(awk '{print $1}' count.txt 2>/dev/null)" = 42 ]''', "wc -l < numbers.txt > count.txt", "wc -l counts lines. Then redirect with >."),
N("h01", "Ask the manual", "Find (with ls --help or man ls) the option that sorts by modification time, then run ls using it.", "",
  r'''echo "$LAST_CMD" | grep -Eq '^ls( +-[a-zA-Z]*t[a-zA-Z]*)+( |$)' ''', "ls -lt", "Read the --help output and look for 'time'."),
N("h02", "Help without Google", "Show only the first 3 lines of the help text of the wc command.", "",
  r'''echo "$LAST_CMD" | grep -q -- '--help' && echo "$LAST_CMD" | grep -q head && echo "$LAST_OUT" | grep -q Usage && [ "$(echo "$LAST_OUT" | grep -c .)" -le 3 ]''', "wc --help | head -3", "cmd --help | head -3"),
N("p01", "Set exact permissions", "Set deploy.sh so the owner can read, write and run it, and everyone else can only read and run it.",
  r'''printf '#!/bin/bash\necho deploy\n' > deploy.sh; chmod 644 deploy.sh''',
  r'''[ "$(stat -c %a deploy.sh)" = 755 ]''', "chmod 755 deploy.sh", "r=4 w=2 x=1. Owner 7, others 5."),
N("u01", "Who am I?", "Print your user name.", "",
  r'''[ "$(echo "$LAST_OUT" | tr -d '[:space:]')" = "$(whoami)" ] && echo "$LAST_CMD" | grep -q whoami''', "whoami"),
N("u02", "Find yourself", "Print ONLY your own line from /etc/passwd.", "",
  r'''echo "$LAST_OUT" | grep -q "^$(whoami):" && [ "$(echo "$LAST_OUT" | grep -c .)" -eq 1 ] && echo "$LAST_CMD" | grep -q grep''', "grep \"^$(whoami):\" /etc/passwd", "grep \"^$(whoami):\" /etc/passwd"),
N("pr01", "Stop the sleeper", "A program 'sleep 7777' is running in the background. Find it and stop it.",
  r'''nohup sleep 7777 >/dev/null 2>&1 </dev/null & sleep 0.5''',
  r'''sleep 0.3; ! pgrep -f '[s]leep 7777' >/dev/null''', "pkill -f '[s]leep 7777'", "pgrep -a sleep shows the PID, then kill PID.",
  cleanup=r'''pkill -f '[s]leep 7777'; true'''),
N("k01", "Is it installed?", "Check whether the package bash is installed, using dpkg.", "",
  r'''echo "$LAST_CMD" | grep -q dpkg && echo "$LAST_OUT" | grep -q 'install ok installed' ''', "dpkg -s bash", "dpkg -s packagename"),
N("k02", "Count packages", "Save how many installed packages have python3 in their name into pycount.txt.", "",
  r'''[ "$(tr -d '[:space:]' < pycount.txt 2>/dev/null)" = "$(dpkg -l | grep python3 | wc -l | tr -d '[:space:]')" ] && [ "$(tr -d '[:space:]' < pycount.txt)" -gt 0 ]''',
  "dpkg -l | grep python3 | wc -l > pycount.txt", "dpkg -l lists packages. Pipe to grep, then wc -l."),
N("k03", "List services", "Show the first 5 running services on your system.", "",
  r'''echo "$LAST_CMD" | grep -q systemctl && [ -n "$LAST_OUT" ]''', "systemctl list-units --type=service --state=running | head -5",
  "systemctl list-units --type=service --state=running | head -5", selftest=False),
N("net01", "Can I reach it?", "Send exactly 2 pings to localhost.", "",
  r'''echo "$LAST_CMD" | grep -q ping && echo "$LAST_OUT" | grep -q '2 received' ''', "ping -c 2 localhost", "-c sets the count.", selftest=False),
N("net02", "Who is listening?", "A web server listens on some port. Show the listening TCP ports and spot it (hint: it is in the 8000s).",
  r'''pkill -f '[h]ttp.server 8082' 2>/dev/null; nohup python3 -m "http.server" 8082 >/dev/null 2>&1 </dev/null & sleep 1''',
  r'''echo "$LAST_CMD" | grep -Eq 'ss |netstat' && echo "$LAST_OUT" | grep -q 8082''', "ss -ltn", "ss -ltn (l=listening, t=tcp, n=numbers)",
  cleanup=r'''pkill -f '[h]ttp.server 8082'; true''', selftest=False),
N("net03", "Read the headers", "Fetch only the HTTP headers of the web server on port 8083 and save them into headers.txt.",
  r'''echo hi > index.html; pkill -f '[h]ttp.server 8083' 2>/dev/null; nohup python3 -m "http.server" 8083 --directory "$LAB" >/dev/null 2>&1 </dev/null & sleep 1''',
  r'''grep -q ' 200 ' headers.txt && grep -qi '^server:' headers.txt''', "curl -sI http://localhost:8083 > headers.txt", "curl -I asks for headers only.",
  cleanup=r'''pkill -f '[h]ttp.server 8083'; true'''),
N("sc01", "Script with an if", "Write greet.sh: with no argument print 'Usage: greet.sh NAME', otherwise print 'Hello, NAME!'.", "",
  r'''[ -f greet.sh ] && [ "$(bash greet.sh 2>&1)" = "Usage: greet.sh NAME" ] && [ "$(bash greet.sh Asha)" = "Hello, Asha!" ]''',
  r'''printf '#!/bin/bash\nif [ -z "$1" ]; then echo "Usage: greet.sh NAME"; else echo "Hello, $1!"; fi\n' > greet.sh''',
  "Open nano with: edit greet.sh. $1 is the first argument; [ -z \"$1\" ] tests for empty."),
N("cr01", "Weekly cron", "Add a cron line to crontab2.txt that runs /opt/report.sh every Monday at 09:00.", "touch crontab2.txt",
  r'''grep -Eq '^0 +9 +\* +\* +(1|Mon|mon) +/opt/report\.sh' crontab2.txt''', "echo '0 9 * * 1 /opt/report.sh' > crontab2.txt", "Weekday: 0 or 7 = Sunday, 1 = Monday."),
N("d01", "How big is it?", "Show the total size of the data folder in human-readable form (like 1.9M).", r'''mkdir data; head -c 2000000 /dev/zero > data/big.bin''',
  r'''echo "$LAST_CMD" | grep -Eq 'du .*-[a-z]*h' && echo "$LAST_OUT" | grep -Eq '^[0-9.]+[KMG]' ''', "du -sh data", "-s summary, -h human-readable."),
N("d02", "Check the memory", "Show memory usage in human-readable form.", "",
  r'''echo "$LAST_CMD" | grep -Eq 'free .*-[a-z]*h' && echo "$LAST_OUT" | grep -q 'Mem:' ''', "free -h", "Read the 'available' column."),
N("ss01", "Make an SSH key", "Create an ed25519 SSH key pair named mykey in this folder with no passphrase.", "",
  r'''[ -f mykey ] && [ -f mykey.pub ] && [ "$(stat -c %a mykey)" = 600 ] && grep -q ssh-ed25519 mykey.pub''', "ssh-keygen -t ed25519 -f mykey -N \"\"", "-f sets the file name, -N the passphrase.", selftest=False),
N("ss02", "Harden SSH config", "In sshd_config.copy set PermitRootLogin and PasswordAuthentication to no. Leave the other lines alone.",
  r'''printf 'Port 22\nPermitRootLogin yes\nPasswordAuthentication yes\nX11Forwarding yes\n' > sshd_config.copy''',
  r'''grep -qx 'PermitRootLogin no' sshd_config.copy && grep -qx 'PasswordAuthentication no' sshd_config.copy && grep -qx 'Port 22' sshd_config.copy && grep -qx 'X11Forwarding yes' sshd_config.copy''',
  r'''sed -i 's/^PermitRootLogin yes/PermitRootLogin no/; s/^PasswordAuthentication yes/PasswordAuthentication no/' sshd_config.copy''', "sed -i 's/old/new/' file"),
]


def M(title, level, teach, ids):
    return dict(title=title, level=level, teach=teach.strip(), ids=ids)


MODULES = [
M("Terminal and moving around", "Beginner", """
The terminal is a window where you control the computer by typing. Think of folders as rooms in a house.
  pwd       shows which room you are in (your full path)
  ls        lists what is in the room  (ls -l = details, ls -a = also hidden files that start with a dot)
  cd name   walks into a folder;  cd ..  goes back out;  cd ~  goes home
A path starting with / begins at the very top of the system. Any other path starts from where you are now.""", ["n01", "n02", "n03"]),
M("Files and folders", "Beginner", """
  mkdir -p a/b/c   create folders (-p also creates the missing parents)
  touch f          create an empty file
  cp a b           copy a to b
  mv a b           move OR rename a to b
  rm f             delete a file;   rm -r dir   delete a folder and everything inside
There is NO recycle bin on Linux. Read every rm command twice before pressing Enter.""", ["f01", "f02", "f03"]),
M("Reading and writing text", "Beginner", """
  echo text > f    write text into a file (overwrites);   >>  adds to the end
  cat f            show a whole file
  head -n 3 f      first 3 lines;   tail -n 3 f   last 3 lines   (tail -f follows a log live)
Config files and logs are just text, so these commands are how you read what a server is doing.""", ["x01", "x02"]),
M("Finding things", "Beginner", """
  grep word file      show lines containing word  (-i ignore case, -n line numbers, -c count, -r whole folder)
  find where -name "pattern"   search folders for file names
  wc -l file          count lines   (wc -l < file prints just the number)
Servers hold thousands of files. These three commands find the needle.""", ["s01", "s02", "s03"]),
M("Getting help", "Beginner", """
Experts look things up all day. You never have to memorise options.
  cmd --help     short guide        man cmd   full manual (press q to quit)
  Tab = auto-complete   Up arrow = previous command   Ctrl+R = search old commands   Ctrl+C = stop a command""", ["h01", "h02"]),
M("Permissions", "Intermediate", """
ls -l shows permissions like -rwxr-xr-x : first the type, then three groups: owner, group, others.
Each group has r (read=4), w (write=2), x (execute=1).  chmod 755 f = rwx for owner, r-x for everyone else.
  chmod +x f   add execute      chmod 600 f   owner only (SSH private keys must be 600)
"Permission denied" is almost always a permissions problem.""", ["p01", "r01", "r11"]),
M("Users", "Intermediate", """
Linux is multi-user.  whoami = your user,  id = user and groups,  groups = your groups.
Admin tasks use  sudo command  (runs ONE command as administrator). Avoid working as root all the time.
All users are listed in /etc/passwd as  name:x:uid:gid:comment:home:shell.""", ["u01", "u02"]),
M("Processes", "Intermediate", """
A running program is a process with a number called a PID.
  ps aux      list all processes       top   live view (q quits)
  pgrep -a name   find PIDs by name    cmd &   run in the background
  kill PID    ask it to stop politely;  kill -9 PID  force it (last resort)
  ss -ltnp    shows which process owns a port""", ["pr01", "r05"]),
M("Pipes and text tools", "Intermediate", """
The pipe  |  sends one command's output into the next. Small tools, combined:
  sort    uniq -c (count repeats; sort first)    cut -d, -f2 (one column)
  awk '{print $1}' (columns, sums)    sed 's/old/new/' (replace; -i edits the file)    diff a b (differences)
Example: grep ERROR app.log | sort | uniq -c | sort -nr | head   = the most repeated errors.
This is how you analyse logs, the daily job of cloud support and SOC analysts.""",
  ["t01", "t02", "t03", "t04", "t05", "r02", "r03", "r12", "r13"]),
M("Packages and services", "Intermediate", """
Software comes in packages. On Ubuntu: sudo apt update, sudo apt install name.
  dpkg -s name   is it installed?      dpkg -l   list all installed packages
Programs that run in the background are services:  systemctl status|start|stop|restart|enable name
Read a service's logs with  journalctl -u name.""", ["k01", "k02", "k03"]),
M("Networking", "Advanced", """
  ping -c 2 host    can I reach it?          ss -ltn   which TCP ports are listening
  curl url          fetch a page;  curl -I url = headers only;  curl -s url -o file = save it
  dig name          test DNS
Debug in this order: can I reach the IP? is the port open? does the application answer?""", ["net01", "net02", "net03", "r06"]),
M("Bash scripting", "Advanced", """
A script is a file of commands. Line 1: #!/bin/bash, then  chmod +x script.sh  and  ./script.sh.
  NAME=Asha; echo $NAME      variables        $1 $2   arguments
  if [ -z "$1" ]; then ...; else ...; fi      decisions
  for x in a b c; do echo $x; done            loops
  while read line; do ...; done < file        read a file line by line
Use  edit file  here to open nano.""", ["r07", "r08", "sc01"]),
M("Backups, cleanup and cron", "Advanced", """
  tar -czf name.tar.gz folder   compressed backup (tar -tzf lists it)
  ln -s target link             shortcut (used to switch releases)
  find . -name "*.log" -mtime +30 -delete   remove old files
cron runs jobs on a schedule:  minute hour day month weekday command
  30 2 * * * /opt/backup.sh   = every day at 02:30.   Edit your jobs with crontab -e.""", ["t06", "t07", "r09", "cr01", "r10"]),
M("Disk, memory and logs", "Advanced", """
  df -h       free disk space             du -sh folder   size of a folder
  du -ah dir | sort -rh | head   the biggest files     ls -lS   sort by size
  free -h     memory (read the 'available' column)
Full disks and low memory are among the most common real incidents. Always look at the biggest thing first.""", ["d01", "d02", "r04"]),
M("Security and git", "Advanced", """
SSH keys replace passwords: ssh-keygen -t ed25519 makes a private key (secret, chmod 600) and a public key (.pub).
Hardening = closing doors: in sshd_config set PermitRootLogin no and PasswordAuthentication no, open only the
firewall ports you need, keep packages updated. Finally, git tracks your work: git init, add, commit, push.""", ["ss01", "ss02", "r14"]),
]
