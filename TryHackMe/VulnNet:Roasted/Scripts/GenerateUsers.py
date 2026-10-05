#!/usr/bin/env python3

from itertools import permutations, product

raw = """
alexawhitehat
jackgoldenhand
tonyskid
johnnyleet
administrator
guest
"""

words = set()

for x in raw.split():
    x = x.strip().lower()

    if "@" in x:
        x = x.split("@")[0]

    if x:
        words.add(x)

people = {
    "alexa": ["alexa", "whitehat"],
    "jack": ["jack", "goldenhand"],
    "tony": ["tony", "skid"],
    "johnny": ["johnny", "leet"],
}

out = set(words)

separators = ["", ".", "_", "-"]

def add_variants(parts):
    parts = [p.lower() for p in parts if p]

    if not parts:
        return

    for p in parts:
        out.add(p)
        out.add(p.upper())
        out.add(p.capitalize())

    for perm in permutations(parts):
        for sep in separators:
            value = sep.join(perm)

            out.add(value)
            out.add(value.lower())
            out.add(value.upper())
            out.add(value.capitalize())

            if len(perm) >= 2:
                initials = "".join(x[0] for x in perm)

                out.add(initials)
                out.add(initials.upper())

                for s in separators:
                    out.add(s.join(x[0] for x in perm))

    if len(parts) >= 2:
        first = parts[0]
        last = parts[-1]

        variants = [
            first[0] + last,
            first + last[0],
            last + first[0],
            last[0] + first,
            first[:2] + last,
            first + last[:2],
            last[:2] + first,
        ]

        for v in variants:
            out.add(v)
            out.add(v.upper())
            out.add(v.capitalize())

            for sep in separators:
                out.add(sep.join([first, last]))
                out.add(sep.join([first[0], last]))
                out.add(sep.join([first, last[0]]))

for name, parts in people.items():
    add_variants(parts)

for word in list(words):
    clean = word.replace("-", "").replace("_", ".").split(".")

    if len(clean) > 1:
        add_variants(clean)

for a, b in product(sorted(words), repeat=2):
    if a == b:
        continue

    if len(a) <= 20 and len(b) <= 20:
        for sep in separators:
            out.add(a + sep + b)
            out.add(b + sep + a)

out = {
    x for x in out
    if x
    and "@" not in x
    and len(x) <= 32
}

with open("Users_combinations.txt", "w") as f:
    for x in sorted(out):
        f.write(x + "\n")

print(f"[+] {len(out)} generated usernames")
print("[+] Saved on Users_combinations.txt")
