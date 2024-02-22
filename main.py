import os
import re
from sys import argv
import tempfile
import toml
from typing import Any, List, Mapping, Optional, Tuple

import git
from git import Repo

# Regex to parse tldr pages as stated in contributing guide
PAGES_REGEX = re.compile(r"\n\s*- (.+?):?\n\n?\s*`([^`]+)`")


def scrape_tldr_github(category: Optional[str] = None) -> List[dict]:
    return scrape_tldr_repo("https://github.com/tldr-pages/tldr.git", category)


def scrape_tldr_repo(url: str, category: Optional[str] = None) -> List[dict[str,str]]:
    tmp_dir = tempfile.mkdtemp()
    repo_path = os.path.join(tmp_dir, "tldr")
    

    print(f"cloning repo {url} to {repo_path}...")
    Repo.clone_from(url, repo_path, depth=1)

    result = []

    print(f"parsing {category}")
    if category:
        sp = os.path.join(repo_path, "pages", category)
        if not os.path.exists(os.path.join(repo_path, "pages", category)):
            raise ValueError(f"Category {category} doesn't exist")
        result.extend(parse_tldr_folder(category, os.path.join(repo_path, "pages", category)))
    else:
        result.extend(parse_tldr_folder("common", os.path.join(repo_path, "pages", "common")))
        # Add other platform-specific folders if needed

    return result


def replace_braces(string):
    if '{{' in string and '}}' in string:
        string = string.replace('{{', '<').replace('}}', '>')

    string = string.replace('"', '""')

    return string



def parse_tldr_folder(category: str, path: str) -> List[dict[str, str]]:
    result = []
    for entry in os.listdir(path):
        entry_path = os.path.join(path, entry)
        #print(entry_path)
        if os.path.isfile(entry_path):
            with open(entry_path, "r") as file:
                result.extend(parse_page(file.read()))
    return result


def parse_page(content: str): #-> List[dict[str, str]]:

    #return [(match.group(1), replace_braces(match.group(2))) for match in PAGES_REGEX.finditer(content)]

    return [ {"description": match.group(1), "command":match.group(2) , "output": ""} for match in PAGES_REGEX.finditer(content)]

    #def print_toml_snippet(description,cmd):
    #    print("[[snippets]]")
    #    print(f"  description = \"{description}\"")
    #    # Print the command
    #    print(f"  command = \"{cmd}\"")
    #    # Print the output (if any)
    #    print("  output = \"\"")  # You can modify this line if needed
    #    # Print a new line to separate each command
    #    print()

if __name__ == "__main__":


    category:str = ""

    categories = ["android","common","freebsd","linux","netbsd","openbsd","osx","sunos","windows"]

    output_file = "./output/snippet.toml"

    if len(argv)>1:

        if argv[1] not in categories:
            print(f"{argv[1]} not a valid category, pass one from ")
            print(','.join(categories))
            exit(0)


        print(f"Selecting category \"{argv[1]}\"")

    else:
        print("defaulting to category \"common\"")
        print("other categories you can pass as argument `python main.py <category>` are:")
        print(','.join(categories))
            
        category = "common"



    commands = scrape_tldr_github(category)

    #data: Mapping[str, List[Mapping[str, Any]]] = {"snippets": commands}


    data = {"snippets": commands}

    print(f"writing to {output_file}")
    with open(output_file, "w") as toml_file:
        toml.dump(data, toml_file)

    #for description, cmd in commands:
    #print_toml_snippet(description,cmd)


    toml.dumps

