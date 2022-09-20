"""precommit.py

Script to invoke as part of a pre-commit hook.
"""

import functools
import re
import shutil
from datetime import date, datetime
from pathlib import Path

# For debug print statements
_filename = Path(__file__).name
print = functools.partial(print, f"[{_filename}]")

# Absolute path to my resumes directory
RESUMES_DIR = Path.home() / "Documents" / "ucla" / "jobs" / "resumes"

# Regex pattern for validating resume filename
R = r"ucla-resume-(\d{2}-\d{2}-\d{4})\.pdf"
RESUME_FILENAME_PATTERN = re.compile(R)

# Regex pattern for finding the existing resume link in my about-me.md
ABOUTME_RESUME_PATTERN = re.compile(rf"\[{R}\]\({R}\)")


def get_recent_resume_path() -> Path | None:
    """Get the path to my most recent resume file. None if none found."""
    recent_path: Path | None = None
    recent_date: date | None = None
    for file in RESUMES_DIR.iterdir():
        match = RESUME_FILENAME_PATTERN.match(file.name)
        if match:
            d = datetime.strptime(match[1], "%m-%d-%Y").date()
            if recent_date is None or recent_date < d:
                recent_path = file
                recent_date = d
    return recent_path


def get_resume_link_pos(content: str) -> tuple[int, int] | None:
    """Get the indices of the resume link in about-me.md, None if DNE."""
    match = ABOUTME_RESUME_PATTERN.search(content)
    if match is None:
        return None
    return (match.start(), match.end())


def update_markdown() -> None:
    """Update the about-me file with a link to my most recent resume."""
    resume = get_recent_resume_path()
    # If for some reason I lost my resumes, do nothing
    if resume is None:
        print(f"WARNING: No resumes found in {RESUMES_DIR}, aborted.")
        return

    # Otherwise copy the most recent one to this repo
    shutil.copy(resume, resume.name)
    print(f"Copied over {resume} to current directory.")
    filename = resume.name

    # Update the link in the file
    with open("about-me.md", "rt+", encoding="utf-8") as fp:
        content = fp.read()
        res = get_resume_link_pos(content)
        # If for some reason the profile has no resume, do nothing
        if res is None:
            print("WARNING: Couldn't find resume link in about-me.md, aborted.")
            return
        start, end = res
        insert_str = f"[{filename}]({filename})"
        new_content = content[:start] + insert_str + content[end:]
        fp.truncate(0)
        fp.seek(0)
        fp.write(new_content)
        print(f"Replaced resume link in about-me.md with {insert_str!r}.")


print(f"Running {_filename} script...")
update_markdown()
print(f"Finished running {_filename}.")
