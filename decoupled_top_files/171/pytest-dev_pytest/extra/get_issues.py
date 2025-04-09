import json

import py
import requests

issues_url = "https://api.github.com/repos/pytest-dev/pytest/issues"


def get_issues():
    """
    Retrieve issues from a GitHub repository.
    
    This function fetches issues from a specified GitHub repository using the GitHub API. It iterates through multiple pages of results until all issues are retrieved. The function uses the `requests` library to make HTTP GET requests and parse the JSON response.
    
    Args:
    None
    
    Returns:
    list: A list of dictionaries representing the issues retrieved from the GitHub repository.
    
    Raises:
    requests.exceptions.RequestException: If there is an error making the HTTP request.
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
    """
    Generates a list of open GitHub issues from a cache file or by fetching them, sorts the issues by their number, and reports on the open issues.
    
    Args:
    args (object): An object containing the following attributes:
    - cache (str): The path to the cache file.
    - refresh (bool): A flag indicating whether to force a refresh of the cache.
    
    Returns:
    None: This function does not return any value. It writes the sorted open issues to the console
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
    
    Args:
    issue (dict): A dictionary containing information about an issue, including its labels.
    
    Returns:
    str: The kind of the issue, which can be one of the following: 'bug', 'enhancement', 'proposal', or 'issue'.
    
    This function extracts the labels from the given issue dictionary and checks if any of them match the predefined keys ('bug', 'enhancement', 'proposal'). If a matching label
    """

    labels = [l["name"] for l in issue["labels"]]
    for key in ("bug", "enhancement", "proposal"):
        if key in labels:
            return key
    return "issue"


def report(issues):
    """
    Reports information about a list of GitHub issues.
    
    Args:
    issues (list): A list of dictionaries containing issue details.
    
    Returns:
    None: This function does not return any value. It prints the issue details to the console.
    
    Summary:
    The function iterates over a list of GitHub issues, extracting and printing the title, kind, status, and link for each issue. It also prints the total number of open issues at the end.
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
