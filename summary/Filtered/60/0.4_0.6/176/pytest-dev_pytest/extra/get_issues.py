import json

import py
import requests

issues_url = "https://api.github.com/repos/pytest-dev/pytest/issues"


def get_issues():
    """
    Retrieve a list of GitHub issues.
    
    This function fetches issues from a GitHub repository using the GitHub API. It iterates through multiple pages of results until all issues are retrieved.
    
    Parameters:
    None
    
    Returns:
    list: A list of dictionaries, where each dictionary represents an issue with keys such as 'title', 'state', 'created_at', etc.
    
    Raises:
    requests.exceptions.RequestException: If there is an error making the HTTP request.
    SystemExit: If the API request limit is
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
    Determine the kind of issue based on its labels.
    
    This function takes an issue object as input and returns the kind of issue
    based on the labels associated with it. The kind can be one of the following:
    - 'bug': if the issue has a 'bug' label.
    - 'enhancement': if the issue has an 'enhancement' label.
    - 'proposal': if the issue has a 'proposal' label.
    - 'issue': if none of the above labels are present.
    """

    labels = [l["name"] for l in issue["labels"]]
    for key in ("bug", "enhancement", "proposal"):
        if key in labels:
            return key
    return "issue"


def report(issues):
    """
    Reports on a list of GitHub issues.
    
    This function iterates over a list of issues and prints details about each one. It extracts the title, kind, status, and number of each issue, and prints a summary for each issue. The function also provides a link to the issue on GitHub.
    
    Parameters:
    issues (list): A list of dictionaries, where each dictionary represents a GitHub issue with keys such as "title", "body", "state", and "number".
    
    Returns:
    None:
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
