#!/usr/bin/env python3
"""Offline self-tests + end-to-end smoke on the fictional persona (tests/fixtures/persona).

    jk test           # ~5 s, no network, no telemetry; exit 0 = all green
Runs in a temporary JOBKIT_HOME, so real me/ and data/ are never touched.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE.parent / "tests" / "fixtures" / "persona"
fails = []


def run(*args, ok=(0,), env=None):
    r = subprocess.run([sys.executable, str(HERE / "jk.py"), *args], capture_output=True, text=True, env=env)
    if r.returncode not in ok:
        fails.append(f"jk {' '.join(args)} -> {r.returncode}: {(r.stdout + r.stderr).strip()[-300:]}")
    return r.stdout


def main() -> int:
    for s in ("tracker.py", "render_cv.py", "text_audit.py"):
        r = subprocess.run([sys.executable, str(HERE / s), "--selftest"], capture_output=True, text=True)
        print(("ok   " if r.returncode == 0 else "FAIL ") + s)
        if r.returncode:
            fails.append(f"{s}: {r.stdout}{r.stderr}")

    home = Path(tempfile.mkdtemp(prefix="jobkit-test-"))
    env = {**os.environ, "JOBKIT_HOME": str(home), "JK_TELEMETRY_OFF": "1"}
    try:
        out = run("setup", env=env)
        assert (home / "me" / "profile.yaml").exists(), "setup did not create me/"
        run("import", str(FIX / "cv.md"), env=env)
        assert (home / "data" / "import" / "cv-cv.txt").exists(), "import failed"
        import yaml
        p = yaml.safe_load((home / "me" / "profile.yaml").read_text())
        p["name"] = "Alex Morgan"
        p["contacts"].update(email="alex.morgan@example.com", phone="+351 900 000 000", city="Lisbon, Portugal")
        p["banned_claims"] = ["machine learning"]
        (home / "me" / "profile.yaml").write_text(yaml.safe_dump(p, sort_keys=False))
        (home / "me" / "experience-bank.md").write_text((FIX / "cv.md").read_text())
        cv = {"header": {"name": "Alex Morgan", "email": "alex.morgan@example.com"}, "title": "Product Manager",
              "summary": "Product manager with 3 years in consumer apps.",
              "experience": [{"company": "Fitly", "role": "Product Manager", "dates": "2023–now",
                              "bullets": ["Grew 7-day retention from 21% to 27%", "Ran 35 user interviews per quarter"]}]}
        (home / "me" / "cv" / "base.yaml").write_text(yaml.safe_dump(cv))
        app = home / "data" / "applications" / "acme-growth"
        app.mkdir(parents=True)
        (app / "cv.yaml").write_text(yaml.safe_dump({"title": "Growth Product Manager", "experience": {"Fitly": [0]},
                                                     "file_name": "Alex Morgan CV"}))
        run("cv", str(app / "cv.yaml"), env=env)
        assert (app / "Alex Morgan CV.docx").exists(), "tailored CV not rendered"
        run("audit", "--kind", "summary", "--text", "Grew retention from 21% to 27%.", env=env)
        run("audit", "--kind", "summary", "--text", "You need me. I did machine learning, +90%.", ok=(1,), env=env)
        run("t", "add", "--company", "Acme", "--role", "Growth PM", "--url", "https://jobs.lever.co/acme/1",
            "--source", "ats:lever", "--score", "8", "--track", "A", env=env)
        run("t", "check", "Acme::Growth PM", "https://jobs.lever.co/acme/1/apply", ok=(1,), env=env)
        run("t", "set", "https://jobs.lever.co/acme/1", "applied", env=env)
        run("t", "set", "https://jobs.lever.co/acme/1", "screening", "recruiter call", env=env)
        run("stats", "--share", env=env)
        share = (home / "data" / "metrics-share.json").read_text()
        assert json.loads(share)["outcome"]["responded"] == 1, "metrics wrong"
        assert "Acme" not in share and "lever.co" not in share, "share leaks company/url"
        assert (home / "data" / "events.jsonl").exists(), "no events logged"
        run("support", "draft", "test ticket", env=env)
        run("setup", "--check", env=env)
        print("ok   e2e persona smoke")
    except AssertionError as e:
        fails.append(f"e2e: {e}")
    finally:
        shutil.rmtree(home, ignore_errors=True)
    for f in fails:
        print("FAIL " + f)
    print("all green" if not fails else f"{len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
