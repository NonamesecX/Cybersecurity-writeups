# SimpleCTF — Writeup

**Difficulty:** Easy  
**Operating System:** Linux

---

## Reconnaissance

### Setup /etc/hosts

Configure local hostname resolution:

![[Machines/TryHackMe/SimpleCTF/Screenshots/etchosts.png]]
### Nmap Scan — Full Port Enumeration

Perform comprehensive port scanning to identify services:

![[Machines/TryHackMe/SimpleCTF/Screenshots/nmap.png]]

**Initial Observations:**

- FTP service with vSFTPd 3.0.3 (allows anonymous login)
- Apache web server on port 80
- SSH on non-standard port 2222

---

## Service Enumeration

### FTP Enumeration — Anonymous Access

Connect to FTP with anonymous credentials:

![[Machines/TryHackMe/SimpleCTF/Screenshots/ftp.png]]

![[ftpfile.png]]

**File Contents:**

![[formitch.png]]

The message suggests:

- System user has a weak password
- Possible username: "mitch" (implied from message context)
- Credentials may be reused across services

### HTTP Reconnaissance

Default apache page on the web application

Enumerate web directories to discover hidden paths:

![[Machines/TryHackMe/SimpleCTF/Screenshots/gobuster.png]]

**Redirect Discovery:**

Accessing `/simple/` reveals a CMS application.

![[Machines/TryHackMe/SimpleCTF/Screenshots/application.png]]

![[versionCMS.png]]

**Application Name:** CMS Made Simple™  
**Version:** 2.2.8  
**Tagline:** "Power for professionals. Simplicity for end users."

There a critical CVE for this CMS version

---

## Vulnerability Analysis

### Identify CVE-2019-9053

![[CVE.png]]

**CVSS Score:** 8.1 (High)  

Search searchsploit CMS Made Simple 2.2.8 vulnerabilities:

![[exploitCMS.png]]


---

## Exploitation

### Prepare Exploit Environment

**Clone/Download Exploit:**

![[searchsploit.png]]

**Set Up Virtual Environment (Python 2 compatibility):**

![[venv.png]]

**Analyze Exploit Code:**

The exploit uses time-based SQL injection to extract:

- User credentials (salt, username, password hash, email)
- Database structure information

Exploit usage:
![[exploitusage.png]]

### Execute SQL Injection Exploit

**Exploit Command:**

```bash
python 46635.py -u http://ctf.lab/simple --crack -w /path/to/rockyou.txt
```

![[Pasted image 20260830221303.png]]


---

## Initial Access

### SSH Access as mitch

Connect via SSH on non-standard port 2222:

```bash
ssh mitch@ctf.lab -p 2222
```

![[Machines/TryHackMe/SimpleCTF/Screenshots/ssh.png]]

/home/mitch:

![[Machines/TryHackMe/SimpleCTF/Screenshots/userflag.png]]

---

## Privilege Escalation

`sudo -l`

![[sudol.png]]

**Analysis:**

- User `mitch` can execute `/usr/bin/vim` as root without password
- This is a critical misconfiguration
- Vim editor allows shell command execution via `:!command` syntax

### Privilege Escalation via Vim

The Vim editor, when executed with sudo privileges, can spawn an interactive shell:

![[vimprivesc.png]]
REFERER:https://hoop.dev/blog/privilege-escalation-in-vim-a-simple-path-to-root

![[root.png]]

