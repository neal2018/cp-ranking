from typing import NamedTuple, List
import requests
import datetime
import os
import json
import time

START_DATE = datetime.datetime(2022, 9, 1)


class Submission(NamedTuple):
    platform: str
    handle: str
    contest_id: int
    problem_id: str
    rating: int
    time: float
    submission_id: int


def get_codeforces(handle: str) -> List[Submission]:
    def validate(submissions):
        def f(submission):
            if submission['verdict'] != 'OK':
                return False
            if submission['creationTimeSeconds'] < START_DATE.timestamp():
                return False
            if submission['contestId'] == 0:
                return False
            if submission['author']['participantType'] not in ('CONTESTANT', 'OUT_OF_COMPETITION'):
                return False
            return True
        return list(filter(f, submissions))

    def unique(submissions):
        res = list()
        solved = set()
        for s in submissions[::-1]:
            key = s['problem']['contestId'], s['problem']['index']
            if key not in solved:
                solved.add(key)
                res.append(s)
        return res[::-1]

    def transform(submissions):
        def f(submission) -> Submission:
            return Submission(
                handle=handle,
                platform="codeforces",
                contest_id=submission['problem']['contestId'],
                problem_id=submission['problem']['index'],
                rating=submission['problem']['rating'] if 'rating' in submission['problem'] else -1,
                time=submission['creationTimeSeconds'],
                submission_id=submission['id'],
            )
        return list(map(f, submissions))

    url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=100000"
    response = requests.get(url)
    submissions = response.json()["result"]
    return transform(unique(validate(submissions)))


def get_atcoder(handle: str) -> List[Submission]:
    difficulties = requests.get(
        "https://kenkoooo.com/atcoder/resources/problem-models.json").json()
    contests = requests.get(
        "https://kenkoooo.com/atcoder/resources/contests.json").json()
    contests = {c['id']: c for c in contests}
    submissions = requests.get(
        f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={handle}&from_second={int(START_DATE.timestamp())}").json()

    def validate(submissions):
        def f(submission):
            if submission['result'] != 'AC':
                return False
            contest = contests[submission['contest_id']]
            if submission['epoch_second'] > contest['start_epoch_second'] + contest['duration_second']:
                return False
            return True
        return list(filter(f, submissions))

    def unique(submissions):
        res = list()
        solved = set()
        for s in submissions[::-1]:
            key = s['problem_id']
            if key not in solved:
                solved.add(key)
                res.append(s)
        return res

    def transform(submissions):
        def f(submission) -> Submission:
            return Submission(
                handle=handle,
                platform="atcoder",
                contest_id=submission['contest_id'],
                problem_id=submission['problem_id'],
                rating=difficulties[submission['problem_id']]['difficulty'],
                time=submission['epoch_second'],
                submission_id=submission['id'],
            )
        return list(map(f, submissions))

    return transform(unique(validate(submissions)))


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def main():
    # read handles from src/handles.json
    base_path = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_path, "src", "data")
    handles = read_json(os.path.join(data_path, "handles.json"))
    # fetch submissions from codeforces and atcoder
    submissions = list()
    for handle in handles:
        for cf_handle in handle["codeforces_handles"]:
            submissions.extend(get_codeforces(cf_handle))
        for ac_handle in handle["atcoder_handles"]:
            submissions.extend(get_atcoder(ac_handle))
        print(f"done {handle}")
        time.sleep(1)
    # transform submissions to json
    submissions = list(map(lambda x: x._asdict(), submissions))
    # write submissions to src/submissions.json
    with open(os.path.join(data_path, "submissions.json"), "w") as f:
        json.dump(submissions, f, indent=2)


if __name__ == "__main__":
    main()
