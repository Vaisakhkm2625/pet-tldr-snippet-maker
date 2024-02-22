import os
import re
import shutil
import tempfile
from typing import List, Optional, Tuple

import git
from git import Repo

# Regex to parse tldr pages as stated in contributing guide
PAGES_REGEX = re.compile(r"\n\s*- (.+?):?\n\n?\s*`([^`]+)`")


def scrape_tldr_github(category: Optional[str] = None) -> List[Tuple[str, str]]:
    return scrape_tldr_repo("https://github.com/tldr-pages/tldr.git", category)


def scrape_tldr_repo(url: str, category: Optional[str] = None) -> List[Tuple[str, str]]:
    tmp_dir = tempfile.mkdtemp()
    repo_path = os.path.join(tmp_dir, "tldr")

    Repo.clone_from(url, repo_path, depth=1)

    result = []

    if category:
        sp = os.path.join(repo_path, "pages", category)
        print(sp)
        if not os.path.exists(os.path.join(repo_path, "pages", category)):
            raise ValueError(f"Category {category} doesn't exist")
        result.extend(parse_tldr_folder(category, os.path.join(repo_path, "pages", category)))
    else:
        result.extend(parse_tldr_folder("common", os.path.join(repo_path, "pages", "common")))
        # Add other platform-specific folders if needed

    return result


def parse_tldr_folder(category: str, path: str) -> List[Tuple[str, str]]:
    result = []
    for entry in os.listdir(path):
        entry_path = os.path.join(path, entry)
        if os.path.isfile(entry_path):
            with open(entry_path, "r") as file:
                result.extend(parse_page(category, file.read()))
    return result


def parse_page(category: str, content: str) -> List[Tuple[str, str]]:
    return [(match.group(1), match.group(2)) for match in PAGES_REGEX.finditer(content)]


if __name__ == "__main__":
    # Example usage:
    commands = scrape_tldr_github("common")
    for description, cmd in commands:
        print(description, "-", cmd)
