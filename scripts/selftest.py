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
        for f in ("interview-mistakes.md", "interview-answers.md", "linkedin.md", "application-answers.md"):
            assert (home / "me" / f).exists(), f"setup did not create me/{f}"
        (home / "me" / "interview-answers.md").write_text("mine")
        run("setup", env=env)
        assert (home / "me" / "interview-answers.md").read_text() == "mine", "setup overwrote me/ on re-run"
        for js, needle in (("formcheck", "empty_count"), ("lijob", "currentJobId")):
            assert needle in run(js, env=env), f"jk {js} prints nothing useful"
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
        assert "sent " in run("t", "today", env=env) and ": 1 (ats 1)" in run("t", "today", env=env), \
            "t today does not count the sent role"
        run("t", "set", "https://jobs.lever.co/acme/1", "screening", "recruiter call", env=env)
        run("stats", "--share", env=env)
        share = (home / "data" / "metrics-share.json").read_text()
        assert json.loads(share)["outcome"]["responded"] == 1, "metrics wrong"
        assert "Acme" not in share and "lever.co" not in share, "share leaks company/url"
        assert (home / "data" / "events.jsonl").exists(), "no events logged"
        run("setup", "--phase", "browser", "--fail", "No Chrome, Alex!", env=env)
        st = json.loads((home / "data" / "setup-state.json").read_text())
        assert "machine" in st["done"] and st["failed"]["browser"] == "no_chrome_alex", "phase state wrong"
        # Telemetry dry run: capture what would be sent, check it carries no personal data.
        probe = ("import sys, json; sys.path.insert(0, %r); import telemetry; out = []; "
                 "telemetry._post = lambda b: out.extend(b) or True; telemetry.tick(); "
                 "telemetry.report_crash('scan.py', ValueError('secret Acme')); print(json.dumps(out))") % str(HERE)
        tenv = {k: v for k, v in env.items() if k != "JK_TELEMETRY_OFF"}
        r = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, env=tenv)
        sent = json.loads(r.stdout or "[]")
        names = [e["event"] for e in sent]
        for need in ("daily_active", "milestone", "monthly_stats", "crash"):
            assert need in names, f"telemetry did not send {need}: {names} {r.stderr[-200:]}"
        blob = json.dumps(sent)
        for leak in ("Acme", "lever.co", "Alex", "alex.morgan", "Fitly", "secret"):
            assert leak not in blob, f"telemetry leaks {leak}"
        prof = home / "me" / "profile.yaml"
        prof.write_text(prof.read_text().replace("telemetry: true", "telemetry: false"))
        r = subprocess.run([sys.executable, "-c", probe.replace("telemetry.tick(); ", "telemetry.tick(); "
                            "telemetry.send('x'); ")], capture_output=True, text=True, env=tenv)
        assert json.loads(r.stdout or "[]") == [], "profile telemetry: false is ignored"
        prof.write_text(prof.read_text().replace("telemetry: false", "telemetry: true"))
        # Regressions from the 0.3.0 review.
        (home / "me" / "cv" / "old.docx").write_bytes(b"PK\x03\x04\xff\xfe binary")
        run("setup", "--check", ok=(0, 1), env=env)                        # binary file in me/ must not crash
        run("import", "--as", "cv", str(FIX / "cv.md"), env=env)
        assert (home / "data" / "import" / "cv-cv.txt").exists(), "import --as cv before the file failed"
        scan_out = home / "data" / "scan_latest.json"
        scan_out.write_text(json.dumps([
            {"company": "Acme", "title": "Growth PM", "url": "https://jobs.lever.co/acme/1", "location": "Remote",
             "age_days": 1, "geo": "wide", "source": "lever"},
            {"company": "Beta", "title": "Product Manager", "url": "https://jobs.lever.co/beta/9", "location": "Remote, Europe",
             "age_days": 1, "geo": "wide", "source": "lever"}]))
        run("scan", "--only", "none", env=env)
        kept = [r["company"] for r in json.loads(scan_out.read_text())]
        assert kept == ["Beta"], f"scan lost the earlier queue or kept a tracked role: {kept}"
        (home / "me" / "boards.txt").write_text("ashby x\n# mine — add your own companies below; always kept\nlever y\n")
        own = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import boards_fit; "
                              "print(boards_fit.own_lines())" % str(HERE)], capture_output=True, text=True, env=env).stdout
        assert own.strip() == "['lever y']", f"boards marker line leaks into own lines: {own}"
        run("support", "draft", "test ticket", env=env)
        ticket = sorted((home / "data" / "support").glob("*.md"))[-1].read_text()
        assert str(Path.home()) not in ticket, "support ticket leaks the home path"
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
