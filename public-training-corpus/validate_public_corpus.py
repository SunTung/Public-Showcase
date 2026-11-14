#!/usr/bin/env python3
"""Offline integrity and publication-boundary check for this public-only subtree."""
import hashlib
import json
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).resolve().parent
BAD_PATH = re.compile(r"(^|/)(?:\.\.|private|secrets?|credentials?|\.github)(/|$)", re.I)
SECRET_MARKER = re.compile(
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    rb"ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|"
    rb"sk-proj-[A-Za-z0-9_-]{20,}|"
    rb"(?im)^\s*(?:api[_-]?key|access[_-]?token|password)\s*[:=]"
)

def validate():
    catalog = json.loads((BASE / "catalog.json").read_text(encoding="utf-8"))
    if catalog.get("schema") != "public_training_corpus_v1":
        raise ValueError("Unsupported catalog schema")
    if catalog.get("auto_publish") is not False:
        raise ValueError("Automatic promotion not allowed")
    ids = set()
    for row in catalog["entries"]:
        if row["id"] in ids:
            raise ValueError("Duplicate document id")
        ids.add(row["id"])
        relative = pathlib.PurePosixPath(row["path"])
        if relative.is_absolute() or BAD_PATH.search(str(relative)):
            raise ValueError("Unsafe corpus path")
        path = BASE.joinpath(*relative.parts)
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(BASE.resolve()):
            raise ValueError("Corpus item missing or outside public subtree")
        data = path.read_bytes()
        if SECRET_MARKER.search(data):
            raise ValueError("Credential signature in public data")
        if row["status"] != "published":
            raise ValueError("Non-published data referenced in public catalog")
        expected = row["git_blob_sha"]
        actual = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        if actual != expected:
            raise ValueError(f"Git blob mismatch: {row['id']}")
        data.decode("utf-8")
    return len(ids)

if __name__ == "__main__":
    n = validate()
    print("PASS public-only corpus metadata and blob integrity:", n)
