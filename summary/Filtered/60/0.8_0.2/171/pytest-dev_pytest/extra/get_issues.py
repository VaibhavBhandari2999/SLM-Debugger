import json

import py
import requests

issues_url = "https://api.github.com/repos/pytest-dev/pytest/issues"


def get_issues():
    issues = []
    url = issues_url
    while 1:
        get_data = {"state": "all"}
        r = requests.get(url, params=get_data)
        data = r.json()
        if r.status_code == 403:
            # API request limit exceeded
            print(data["message"])
            exit(1)
        issues.extend(data)

        # Look for next page
        links = requests.utils.parse_header_links(r.headers["Link"])
        another_page = False
        for link in links:
            if link["rel"] == "next":
                url = link["url"]
                another_page = True
        if not another_page:
            return issues


def main(args):
    """
    Function to manage GitHub issues.
    
    This function reads or writes a cache file of GitHub issues based on the provided arguments. It checks if the cache file exists and whether a refresh is requested. If either condition is true, it fetches the latest issues from GitHub. Otherwise, it reads the cached issues. The function then filters and sorts the issues, and finally reports on the open issues.
    
    Parameters:
    args (argparse.Namespace): An object containing command-line arguments. Expected attributes are:
    - cache
    """

    cachefile = py.path.local(args.cache)
    if not cachefile.exists() or args.refresh:
        issues = get_issues()
        cachefile.write(json.dumps(issues))
    else:
        issues = json.loads(cachefile.read())

    open_issues = [x for x in issues if x["state"] == "open"]

    open_issues.sort(key=lambda x: x["number"])
    report(open_issues)


def _get_kind(issue):
    """
    Get the kind of an issue based on its labels.
    
    This function determines the kind of an issue by examining its labels. It checks for the presence of specific keywords in the labels and returns the corresponding kind. If none of the specified keywords are found, it returns 'issue' as the default kind.
    
    Parameters:
    issue (dict): A dictionary representing an issue, which should contain a 'labels' key with a list of label names.
    
    Returns:
    str: The kind of the issue, which can be
    """

    labels = [l["name"] for l in issue["labels"]]
    for key in ("bug", "enhancement", "proposal"):
        if key in labels:
            return key
    return "issue"


def report(issues):
    """
    Report on a list of GitHub issues.
    
    This function iterates over a list of issues and prints details about each one.
    Each issue is expected to be a dictionary containing at least the following keys:
    - 'title': The title of the issue.
    - 'body': The body of the issue (optional).
    - 'state': The current state of the issue (e.g., 'open', 'closed').
    - 'number': The issue number.
    
    Parameters:
    issues (list): A list of dictionaries
    """

    for issue in issues:
        title = issue["title"]
        # body = issue["body"]
        kind = _get_kind(issue)
        status = issue["state"]
        number = issue["number"]
        link = "https://github.com/pytest-dev/pytest/issues/%s/" % number
        print("----")
        print(status, kind, link)
        print(title)
        # print()
        # lines = body.split("\n")
        # print("\n".join(lines[:3]))
        # if len(lines) > 3 or len(body) > 240:
        #    print("...")
    print("\n\nFound %s open issues" % len(issues))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("process bitbucket issues")
    parser.add_argument(
        "--refresh", action="store_true", help="invalidate cache, refresh issues"
    )
    parser.add_argument(
        "--cache", action="store", default="issues.json", help="cache file"
    )
    args = parser.parse_args()
    main(args)
