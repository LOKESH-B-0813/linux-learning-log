# Real-world Linux questions (answer out loud, then check the outline)

1. **The server is slow. What do you check first?** `uptime` (load), `top`/`htop` (CPU, memory), `free -h`, `df -h`, `iostat`/`vmstat`, `dmesg`, then app logs.
2. **Disk is at 100%. How do you find the cause?** `df -h`, then `du -xh / | sort -rh | head`. Also check deleted-but-open files (`lsof +L1`) and inodes (`df -i`).
3. **"No space left on device" but `df -h` shows free space. Why?** Inodes are exhausted (millions of tiny files). Confirm with `df -i`.
4. **A service will not start. Steps?** `systemctl status svc`, `journalctl -u svc -xe`, test the config (`nginx -t`), check port conflicts (`ss -ltnp`), file permissions, then recent changes.
5. **You cannot SSH into a server. Troubleshoot.** Reachability (`ping`, `nc -vz host 22`), firewall/security group, sshd running, key permissions (600), correct user, `~/.ssh/authorized_keys` permissions, `ssh -vvv`.
6. **Which process is using port 80?** `ss -ltnp | grep :80` or `lsof -i :80`.
7. **A script works manually but fails in cron. Why?** Minimal PATH/environment, relative paths, wrong permissions, no output captured. Use absolute paths and redirect output to a log.
8. **Hard link vs symbolic link?** A hard link is another name for the same inode (same filesystem, survives deletion of the original). A symlink is a pointer to a path that breaks if the target moves.
9. **What happens when Linux boots?** Firmware (BIOS/UEFI), bootloader (GRUB), kernel, init/systemd, targets and services, login.
10. **Explain 755, 644 and 600.** rwxr-xr-x (programs/folders), rw-r--r-- (normal files), rw------- (private keys). Digits: owner, group, others.
11. **Zombie vs orphan process?** Zombie: finished but the parent has not collected its exit status. Orphan: parent died and init adopts it.
12. **`kill` vs `kill -9`?** SIGTERM asks the process to shut down cleanly; SIGKILL cannot be caught and can leave temp files or corrupt data. Try TERM first.
13. **Find files over 100 MB modified more than 30 days ago.** `find / -type f -size +100M -mtime +30 2>/dev/null`
14. **How do you see who logged in, and failed logins?** `who`, `last`, `lastb`, and `/var/log/auth.log` (or `/var/log/secure` on RHEL).
15. **What is load average?** Average number of runnable (and waiting) tasks over 1, 5 and 15 minutes. Compare it with the number of CPU cores.
16. **How do you read `free -h`?** Look at the "available" column, not "free". Linux uses spare RAM as cache. If memory is truly short, check `dmesg` for the OOM killer.
17. **DNS is not resolving. Debug it.** `dig`/`nslookup`, `/etc/resolv.conf`, try `curl` by IP vs by name to isolate DNS from network problems.
18. **How do you patch a production server safely?** Backup or snapshot, test in staging, `apt update && apt upgrade`, schedule a window, reboot if needed, verify services, keep a rollback plan.
19. **Create a user with sudo and key-only login.** `useradd -m -s /bin/bash u`, `usermod -aG sudo u`, put the public key in `~u/.ssh/authorized_keys` (dir 700, file 600).
20. **Harden SSH.** Disable root login and password auth, use keys, restrict users, firewall the port, fail2ban, keep OpenSSH updated, MFA where possible.
21. **Explain:** `grep ERROR app.log | sort | uniq -c | sort -nr | head`. Filters ERROR lines, groups identical ones, counts them, sorts by count, and shows the top 10.
22. **What does `/etc/fstab` do?** Lists filesystems to mount at boot. A bad entry can stop the boot, so test with `mount -a` before rebooting.
23. **cron vs systemd timers?** Cron is simple and universal. Timers give logging through journald, dependencies and catch-up after downtime.
24. **A process is eating 100% CPU. What do you do?** Identify it (`top`, `ps aux --sort=-%cpu`), inspect (`strace -p`, logs), restart or throttle (`nice`/`cgroups`) and find the root cause.
