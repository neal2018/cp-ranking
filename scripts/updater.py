import datetime
import json
import os
import time
import re
import pytz
from typing import List, NamedTuple
from collections import defaultdict
import random
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import requests
import pyaes
from bs4 import BeautifulSoup

os.environ["CF_USERNAME"] = "cheetahbot"
os.environ["CF_PASSWORD"] = "bottings5!"
moscow_tz = pytz.timezone('Europe/Moscow')
ny_tz = pytz.timezone('US/Eastern')
utc_tz = pytz.timezone('UTC')

START_DATE = datetime.datetime(2023, 9, 5, tzinfo=ny_tz)
END_DATE = datetime.datetime(2023, 12, 22, hour=23, minute=59, second=59, tzinfo=ny_tz)

contests = {}
divisions = {}
unrated_contests = set()

with open("./scripts/unrated_contests.txt") as f:
    for contest in f:
        unrated_contests.add(int(contest))

class Submission(NamedTuple):
    platform: str
    handle: str
    contest_id: str
    problem_id: str
    rating: int
    division: int
    submission_id: int
    time: int
    solved: bool
    upsolved: bool

def get_json(url, retries=10):
    for i in range(retries):
        response = requests.get(url)
        try:
            json_result = response.json()
            return json_result
        except json.decoder.JSONDecodeError:
            print(f"failed attempt {i}")
            if i == 9:
                exit(1)
            time.sleep(5)

url = f"https://codeforces.com/api/contest.list?gym=false"
for contest in get_json(url)['result']:
    contest_id = contest['id']
    if contest_id in unrated_contests:
        continue;
    contests[contest_id] = contest['startTimeSeconds'] + contest['durationSeconds']
    contest_name = contest['name'].lower()
    if "div. 2" in contest_name:
        divisions[contest_id] = 2
    elif "div. 1" in contest_name:
        divisions[contest_id] = 1
    elif "div. 3" in contest_name:
        divisions[contest_id] = 3
    elif "div. 4" in contest_name:
        divisions[contest_id] = 4
    else:
        divisions[contest_id] = 2
    contests[contest['id']] = contest['startTimeSeconds'] + contest['durationSeconds']


def get_codeforces(handle: str) -> List[Submission]:
    def validate(submissions):
        def f(submission):
            if not submission.get('verdict'): # in case this runs mid-contest and encounters un-judged submissions
                return False
            if submission['verdict'] != 'OK':
                return False
            if submission['creationTimeSeconds'] < START_DATE.timestamp():
                return False
            if submission['creationTimeSeconds'] > END_DATE.timestamp():
                return False
            if not submission.get('contestId'):
                return False
            if not contests.get(submission['contestId']):
                return False
            # if submission['creationTimeSeconds'] - contests[submission['contestId']] > 604800:
            #     return False
            if submission['creationTimeSeconds'] > contests[submission['contestId']]: # no upsolves
                return False
            if submission['author']['participantType'] not in {'CONTESTANT', 'OUT_OF_COMPETITION', 'PRACTICE', 'VIRTUAL'}:
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
                division=divisions[submission['problem']['contestId']],
                submission_id=submission['id'],
                time=submission['creationTimeSeconds'],
                solved=True,
                upsolved=submission['creationTimeSeconds'] > contests[submission['contestId']]
            )
        return list(map(f, submissions))

    url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=100000"
    response_json = get_json(url)
    if not response_json.get("result"):
        print(f"couldn't get results for {handle}")
        return []
    submissions = response_json["result"]
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


class CFLogin:
    BASE = "https://codeforces.com"
    service_url = f"{BASE}/enter"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    def __enter__(self):
        self.driver.get(self.service_url)
        username_field = self.driver.find_element(by=By.ID, value="handleOrEmail")
        password_field =self.driver.find_element(by=By.ID, value="password")
        login_button = self.driver.find_element(by=By.XPATH, value='//*[@id="enterForm"]/table/tbody/tr[4]/td/div[1]/input')
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        login_button.click()
        time.sleep(5)
        return self

    def __exit__(self, etype, value, traceback):
        pass

    def navigate(self, url):
        self.driver.get(url)
        # time.sleep(3)

    def get_content(self):
        
        datatable_xpath = '//*[@id="pageContent"]/div[2]/div[6]/table'
        mytable = None
        while True:
            try:
                mytable = self.driver.find_element("xpath", datatable_xpath)
                break
            except selenium.common.exceptions.NoSuchElementException:
                time.sleep(0.1)
        rows = [[cell.text for cell in row.find_elements(By.TAG_NAME, 'td')] for row in mytable.find_elements(By.CSS_SELECTOR, 'tr')]
        return rows

    def get_rcpc(self, dt):
        matched = re.findall(r'toNumbers\("(.+?)"\)', dt)
        assert len(matched) == 3
        key, iv, text = matched
        key = bytes.fromhex(key)
        iv = bytes.fromhex(iv)
        block = pyaes.AESModeOfOperationCBC(key, iv)
        rcpc = block.decrypt(bytes.fromhex(text)).hex()
        return rcpc


def get_group(handles: List[str], group, contests, allow_unsolved=False):

    profile_str = "href=\"/profile/"
    team_str = "<td class=\\status-party-cell\""
    team_end_str = "</td>"
    verdict_str = "submissionverdict=\""
    problem_str = "a href=\""
    time_str = "<span class=\"format-time\" data-locale=\"en\">"
    start = "<div class=\"datatable\" " + \
        "style=\"background-color: #E1E1E1; padding-bottom: 3px;\">"
    
   

    def get_token(data, start, end):
        pos = data.find(start)
        data = data[pos + len(start):]
        pos = data.find(end)
        tok = data[:pos]
        data = data[pos:]
        return (data, tok)

    def get_usernames(team):
        usernames = []
        while profile_str in team:
            team, names = get_token(team, profile_str, "\"")
            usernames.append(names)
        return sorted(usernames)

    all_handles = [item.lower() for sublist in handles for item in sublist]

    errors = ["login - codeforces", "internal server error", "web server is down", "web server is returning an unknown error"]

    with CFLogin(os.environ["CF_USERNAME"], os.environ["CF_PASSWORD"]) as cf:
        time.sleep(3)
        submissions = list()
        for contest in contests:
            print(contest)
            contest_name = contest["name"]
            contest_start = moscow_tz.localize(datetime.datetime.strptime(
                contest["start"], "%b/%d/%Y %H:%M")).astimezone(utc_tz)
            contest_end = moscow_tz.localize(datetime.datetime.strptime(
                contest["end"], "%b/%d/%Y %H:%M")).astimezone(utc_tz)
            contest_multiplier = contest["multiplier"]
            solved = defaultdict(lambda: [None, None]) # store (wa, ac)
            index = 1
            need_break = False
            prev = set()
            retries = 0
            while not need_break:
                if retries == 10:
                    print("Too many retries")
                    exit(1)
                curr = set()
                submission_url = f"{cf.BASE}/{contest_name}/status?pageIndex={index}&order=BY_JUDGED_DESC"
                cf.navigate(submission_url)
                time.sleep(3)
                data = cf.get_content()
                fetched_cnt = 0
                for row in data:
                    if not row:
                        continue
                    tm = row[1]
                    print(tm)
                    if tm.endswith("UTC-4") or tm.endswith("UTC-5"):
                        tm = tm[:-5]
                    print(tm)
                    usernames = row[2].split(": ")[-1].split(", ")
                    problem = row[3]
                    verdict = row[5]
                    dt = moscow_tz.localize(datetime.datetime.strptime(tm, "%b/%d/%Y %H:%M")).astimezone(utc_tz)
                    curr.add((tuple(usernames), dt))
                    fetched_cnt += 1
                    if dt > END_DATE.astimezone(utc_tz):
                        continue
                    if dt < contest_start:
                        need_break = True
                        break
                    is_solved = verdict == 'Accepted'
                    if not allow_unsolved and not is_solved:
                        continue
                    for uname in usernames:
                        if uname.lower() in all_handles:
                            timestamp = int(dt.timestamp())
                            if solved[(uname, problem)][int(is_solved)] is None:
                                solved[(uname, problem)][int(is_solved)] = timestamp
                            elif timestamp < solved[(uname, problem)][int(is_solved)]:
                                solved[(uname, problem)][int(is_solved)] = timestamp
                print(
                    f"fetched total: {len(solved)} current page: {index}, {fetched_cnt}")
                index += 1
                if not fetched_cnt or curr == prev:
                    print("broke here", len(solved), fetched_cnt, curr==prev)
                    break
                prev = curr
            for (uname, problem), (wa_timestamp, ac_timestamp) in sorted(solved.items(), key=lambda x: min([y for y in x[1] if y is not None])):
                if wa_timestamp is not None and allow_unsolved and wa_timestamp <= contest_end.timestamp():
                    submissions.append(Submission(
                        handle=uname,
                        platform=group,
                        contest_id=contest_name,
                        problem_id=problem,
                        division=contest_multiplier,
                        solved=False,
                        upsolved=(wa_timestamp > contest_end.timestamp()),
                        rating=int(wa_timestamp <= contest_end.timestamp() + 604800),
                        time=wa_timestamp,
                        submission_id=contest_start.timestamp(),
                    ))
                if ac_timestamp is not None and ac_timestamp <= contest_end.timestamp() + 604800:
                    submissions.append(Submission(
                        handle=uname,
                        platform=group,
                        contest_id=contest_name,
                        problem_id=problem,
                        division=contest_multiplier,
                        solved=True,
                        upsolved=(ac_timestamp > contest_end.timestamp()),
                        rating=int(ac_timestamp <= contest_end.timestamp() + 604800),
                        time=ac_timestamp,
                        submission_id=contest_start.timestamp(),
                    ))
            print(f"done {contest_name}")
        return submissions


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def main():
    # read data from src/data/
    base_path = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_path, "src", "data")
    handles = read_json(os.path.join(data_path, "handles.json"))
    icpc_contests = read_json(os.path.join(data_path, "icpcs.json"))
    zealots_contests = read_json(os.path.join(data_path, "zealots.json"))

    submissions = list()

    # # handle codeforces and atcoder
    # # print("starting handling codeforces and atcoder")
    # print("starting handling codeforces")
    # for handle in handles:
    #     num = random.uniform(10, 20)
    #     time.sleep(num)
    #     for cf_handle in handle["codeforces_handles"]:
    #         submissions.extend(get_codeforces(cf_handle))
    #     # for ac_handle in handle["atcoder_handles"]:
    #     #     submissions.extend(get_atcoder(ac_handle))
    #     print(f"done {handle}")
    #     time.sleep(1)

    # handle icpc
    print("starting handling icpc")
    cf_handles = [handle["codeforces_handles"] for handle in handles]
    submissions.extend(get_group(cf_handles, "icpc", icpc_contests, allow_unsolved=False))
    print(f"fetched {len(submissions)} submissions from icpc")

    # handle zealots
    print("starting handling zealots")
    cf_handles = [handle["codeforces_handles"] for handle in handles]
    submissions.extend(get_group(cf_handles, "zealots", zealots_contests, allow_unsolved=False))
    print(f"fetched {len(submissions)} submissions from zealots")

    # transform submissions to json
    submissions = list(map(lambda x: x._asdict(), submissions))
    submissions.sort(key=lambda x : (x["platform"], x["handle"], x["time"]))
    # write submissions to src/submissions.json
    with open(os.path.join(data_path, "submissions.json"), "w") as f:
        json.dump(submissions, f, indent=2)


if __name__ == "__main__":
    main()
