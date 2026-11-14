#!/usr/bin/env python3
"""Download only explicitly released public corpus files, with SHA verification."""
import argparse
import hashlib
import json
import pathlib
import re
import urllib.request

BASE_URL = "https://raw.githubusercontent.com/SunTung/Public-Showcase/main/public-training-corpus/"
ALLOWED_NAME = re.compile(r"^texts/[a-z0-9][a-z0-9_-]*\.txt$")

def download(url, max_bytes):
    request = urllib.request.Request(url, headers={"User-Agent":"public-training-corpus/1.0"})
    with urllib.request.urlopen(request, timeout=35) as response:
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("Oversized public corpus file")
    return data

def git_blob_sha(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Destination folder for public text only")
    parser.add_argument("--list", action="store_true", help="List released items without downloading texts")
    args = parser.parse_args()
    manifest = json.loads(download(BASE_URL+"catalog.json", 1024*1024))
    if manifest.get("schema") != "public_training_corpus_v1":
        raise ValueError("Unknown catalog schema")
    dest = pathlib.Path(args.out)
    seen = set()
    for entry in manifest.get("entries", []):
        name = entry["path"]
        if not ALLOWED_NAME.fullmatch(name) or name in seen:
            raise ValueError("Unsafe or duplicated path in public release")
        seen.add(name)
        if entry.get("status") != "published" or entry.get("training_approved_for_external_ingestion") is not True:
            continue
        if args.list:
            print(entry["id"], name, entry.get("language"))
            continue
        body = download(BASE_URL+name, 5*1024*1024)
        if git_blob_sha(body) != entry["git_blob_sha"]:
            raise ValueError("Downloaded content failed SHA validation")
        body.decode("utf-8")
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        # Never silently overwrite a user's existing training material.
        with target.open("xb") as f:
            f.write(body)
        print("Verified", entry["id"], len(body), "bytes")

if __name__ == "__main__":
    main()
