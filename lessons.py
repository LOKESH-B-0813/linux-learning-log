"""Lesson bank. Each lesson = setup script, task text, check script, answer.
The check script runs after EVERY command you type. Exit code 0 = passed.
Env available to scripts: $LAB (lesson folder), $LAST_CMD, $LAST_OUT, $CWD.
To add a lesson: copy any L(...) block below and edit it."""


def L(id, level, title, task, setup, check, answer, hint, why, **kw):
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
  "", r'''echo "$LAST_OUT" | grep -q '10\.0\.0\.9' && echo "$LAST_CMD" | grep -Eq 'uniq|awk' && [ "$(echo "$LAST_OUT" | wc -l)" -le 3 ]''',
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
