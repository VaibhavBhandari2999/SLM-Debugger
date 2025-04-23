import json

import py
import requests

issues_url = "https://api.github.com/repos/pytest-dev/pytest/issues"


def get_issues():
    """
    Retrieve a list of issues from a GitHub repository.
    
    This function fetches issues from a GitHub repository using the GitHub API. It iterates through multiple pages of results if necessary.
    
    Parameters:
    None (the function uses a global variable `issues_url` for the API endpoint).
    
    Returns:
    list: A list of dictionaries, where each dictionary represents an issue with keys such as 'number', 'title', 'state', 'created_at', 'updated_at', and 'body'.
    
    Raises:
    requests
    """

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
    Determine the kind of an issue based on its labels.
    
    This function takes an issue object as input and returns the kind of the issue
    based on the presence of specific labels. The kind can be one of 'bug', 'enhancement', 'proposal', or 'issue'.
    
    Parameters:
    issue (dict): A dictionary representing an issue, which includes a list of labels under the key 'labels'.
    
    Returns:
    str: The kind of the issue ('bug', 'enhancement', 'proposal', or
    """

    labels = [l["name"] for l in issue["labels"]]
    for key in ("bug", "enhancement", "proposal"):
        if key in labels:
            return key
    return "issue"


def report(issues):
    """
    Reports a summary of open issues from a GitHub issue tracker.
    
    This function iterates over a list of issues and prints a summary of each issue. The summary includes the issue's status, kind, and title. It also provides a link to the issue on GitHub.
    
    Parameters:
    issues (list): A list of dictionaries, where each dictionary represents an issue with keys such as "title", "body", "state", and "number".
    
    Returns:
    None: This function does not return any value. It
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
