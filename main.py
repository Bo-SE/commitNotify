from git.repo import Repo
from os import mkdir, listdir
from os.path import exists, join
from telebotapi import TelegramBot
from secrets import bot_token
from time import sleep
from datetime import datetime, timedelta


def exit_empty():
    print("Clone repositories into the \"repos\" to track them")
    exit()


def escape(string):
    out = ""
    for c in string:
        if c in "`~!@#$%^&*()_+-=[]{};':\"<>,./?":
            out += f"\\"
        out += c
    return out


def mess(repo, commit):
    repo_url = list(repo.remote().urls)[0].replace('.git', '')
    repo_sha = commit.name_rev.split()[0]
    body = f"New commit on " \
           f"**[{escape(repo_url.replace('https://github.com/', ''))}]" \
           f"({escape(repo_url)})** " \
           f"by **{escape(str(commit.committer))}**: {escape(commit.summary)}\n\n" \
           f"Full message:\n" \
           f"```\n{escape(commit.message)}```\n" \
           f"Commit code: [{repo_sha[:7]}]({escape(repo_url)}/commit/{escape(repo_sha)})"
    print(body[200:].encode())
    print(body[219].encode())
    print(body)
    t.sendMessage(
        GROUP,
        body,
        parse_mode="MarkdownV2")


GROUP = TelegramBot.Chat.by_id(-898976111)


if __name__ == "__main__":
    t = TelegramBot(bot_token, safe_mode=True)
    t.bootstrap()

    if not exists("repos"):
        mkdir("repos")
        exit_empty()

    repos = []
    folds = listdir("repos")
    if not folds:
        exit_empty()

    for i in folds:
        repos.append(Repo.init(join("repos", i)))

    while True:
        for i in repos:
            latest_commit = i.commit()
            i.remote().pull()
            for j in i.iter_commits(since=latest_commit.committed_date + 1):
                mess(i, j)
        print(f"Next check will occur on {datetime.now() + timedelta(seconds=120)}")
        sleep(30)
