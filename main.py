import argparse
import logging
import os
import time

import requests
import yaml

class Request:
    """Request class will hold all the information for a specific request."""

    def __init__(self, name, url, method="GET", headers={}, body=""):
        self.name = name
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body
        self.responses = []
        self.up_responses = 0
        self.number_of_requests = 0

    def __str__(self):
        return f"name: '{self.name}', url: '{self.url}', method: '{self.method}', headers: '{self.headers}', body: '{self.body}', up_responses: {self.up_responses}, number_of_requests: {self.number_of_requests}"


def parse_yaml(filename):
    """Parse yaml file and return a list of Request objects."""
    requests = []
    with open(filename) as stream:
        for request in yaml.safe_load(stream):
            name = request["name"]
            url = request["url"]
            method = request.get("method", "GET")
            headers = request.get("headers", {})
            body = request.get("body", "")

            req = Request(name, url, method, headers, body)
            requests.append(req)

    return requests


def make_all_requests(requests_list):
    """This function will make HTTP requests for all request objects found in requests_list and saving information in Request object."""
    for req in enumerate(requests_list):
        req.number_of_requests = req.number_of_requests + 1
        try:
            result = requests.request(
                req.method, req.url, data=req.body, headers=req.headers
            )

            req.responses.append(result)
            if up_or_down(result) is True:
                req.up_responses = req.up_responses + 1
        except requests.exceptions.ConnectionError:
            continue
    return requests_list


def up_or_down(response):
    """Determine if the response is considered UP (True) or DOWN (False)."""

    # 500000 is 500 millisecond. range is inclusive of the start (200) but not the stop (300).
    if response.elapsed.microseconds < 500000 and response.status_code in range(
        200, 300
    ):
        return True
    else:
        return False


def log_results(requests_list):
    for r in requests_list:
        availability = 100 * (r.up_responses / r.number_of_requests)
        logging.info(f"{r.url} has {availability}% availability percentage")
        logging.debug(r)


if __name__ == "__main__":
    if os.environ.get("DEBUG"):
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level)

    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", "-f", default="test.yaml")
    parser.add_argument("--timeout", default=15, type=int)
    args = parser.parse_args()

    requests_list = parse_yaml(args.filename)

    while True:
        requests_list = make_all_requests(requests_list)
        log_results(requests_list)
        time.sleep(args.timeout)
