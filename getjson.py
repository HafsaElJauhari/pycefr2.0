"""
PROGRAM TO OBTAIN SUMMARIES FROM JSON
"""

import json
import os
import re
import tabulate

# Dictionary of all repositories and files
dict_total = {}
# Dictionary of all repositories
dict_summary = {}
# Dictionary of all files
dict_repo = {}


def extract_levels(data):
    """Extract repository levels."""
    # Take out the repositories
    for repo in data.keys():
        dict_total[repo] = {}
        dict_repo[repo] = {}
        for file in data[repo]:
            dict_total[repo][file] = {}
            for i in data[repo][file]:
                level = i['Level']
                if 'Levels' not in dict_summary:
                    dict_summary['Levels'] = {}
                ini_total('Levels', level)
                if 'Levels' not in dict_repo[repo]:
                    dict_repo[repo]['Levels'] = {}
                ini_repo(repo, 'Levels', level)
                if 'Levels' not in dict_total[repo][file]:
                    # Initialize the dictionary values to 0
                    # Create the 'Levels' key
                    dict_total[repo][file]['Levels'] = {}
                ini_values(repo, file, 'Levels', level)
                clase = i['Class']
                # Remove numbers
                clase = re.sub(r"\s?\d", "", clase)
                if 'Class' not in dict_summary:
                    dict_summary['Class'] = {}
                ini_total('Class', clase)
                if 'Class' not in dict_repo[repo]:
                    dict_repo[repo]['Class'] = {}
                ini_repo(repo, 'Class', clase)
                if 'Class' not in dict_total[repo][file]:
                    # Initialize the dictionary values to 0
                    # Create the 'Class' key
                    dict_total[repo][file]['Class'] = {}
                ini_values(repo, file, 'Class', clase)

        write_results(repo)


def ini_total(type, key):
    """Initialize or increment values."""
    if key not in dict_summary[type]:
        if key != "":
            dict_summary[type][key] = 1
    else:
        dict_summary[type][key] += 1


def ini_repo(repo, type, key):
    """Initialize or increment values."""
    if key not in dict_repo[repo][type]:
        if key != "":
            dict_repo[repo][type][key] = 1
    else:
        dict_repo[repo][type][key] += 1


def ini_values(repo, file, type, key):
    """Initialize or increment values."""
    if key not in dict_total[repo][file][type]:
        if key != "":
            dict_total[repo][file][type][key] = 1
    else:
        dict_total[repo][file][type][key] += 1


def write_results(repo):
    """Create a .txt file with a summary of results."""
    # Get current path
    wd = os.getcwd()
    # Create new folder
    try:
        os.mkdir(wd + "/DATA_JSON")
    except FileExistsError:
        pass
    # Create a file for each repository
    name_file = wd + "/DATA_JSON/" + repo + '.json'
    repository = {repo: dict_total[repo]}
    with open(name_file, 'w', encoding='utf-8') as file:
        json.dump(repository, file, indent=4)
    # Create a total file
    name_file = wd + "/DATA_JSON/total_data.json"
    with open(name_file, 'w', encoding='utf-8') as file:
        json.dump(dict_total, file, indent=4)
    # Create a summary data
    name_file = wd + "/DATA_JSON/summary_data.json"
    with open(name_file, 'w', encoding='utf-8') as file:
        json.dump(dict_summary, file, indent=4)
    # Create a repo data
    name_file = wd + "/DATA_JSON/repo_data.json"
    with open(name_file, 'w', encoding='utf-8') as file:
        json.dump(dict_repo, file, indent=4)


def show_results():
    """Returns the result of the analysis."""
    table_headers = ['REPO NAME', 'FILE', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    table_data = []

    level_totals = {level: 0 for level in table_headers[2:]}
    total_files = 0

    for repo, files in dict_total.items():
        for file, levels in files.items():
            row = [repo, file]
            total_files += 1
            for level in table_headers[2:]:
                count = levels['Levels'].get(level, 0)
                row.append(count)
                # Add to the total for the current level
                level_totals[level] += count
            table_data.append(row)

    # Add the total row at the end
    total_row = ['TOTAL', f'{total_files} files']
    for level in table_headers[2:]:
        total_count = level_totals[level]
        total_row.append(total_count)
    table_data.append(total_row)

    result = tabulate.tabulate(table_data, headers=table_headers, tablefmt='grid')
    return result

def read_json():
    """Read json file."""
    with open('data.json', encoding='utf-8') as file:
        data = json.load(file)
        extract_levels(data)
        result = show_results()
        return result


if __name__ == "__main__":
    read_json()
