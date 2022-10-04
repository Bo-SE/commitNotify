from git.repo import Repo
from os import mkdir, listdir
from os.path import exists, join
from telebotapi import TelegramBot
from secrets import bot_token
from time import sleep
from datetime import datetime, timedelta
from json import load, dump


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


def sha(commit):
    return commit.name_rev.split()[0]


def mess(repo, commit):
    repo_url = list(repo.remote().urls)[0].replace('.git', '')
    body = f"New commit on " \
           f"**[{escape(repo_url.replace('https://github.com/', ''))}]" \
           f"({escape(repo_url)})** " \
           f"by **{escape(str(commit.committer))}**: _{escape(commit.summary)}_\n\n" \
           f"Full message:\n" \
           f"```\n{escape(commit.message)}```\n" \
           f"Commit code: [{sha(commit)[:7]}]({escape(repo_url)}/commit/{escape(sha(commit))})"
    t.sendMessage(
        GROUP,
        body,
        parse_mode="MarkdownV2")


GROUP = TelegramBot.Chat.by_id(-898976111)


if __name__ == "__main__":
    try:
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

        if not exists("data.json"):
            dump({}, open("data.json", "w+"))
        data = load(open("data.json"))


        def ddump():
            dump(data, open("data.json", "w+"))


        while True:
            for i in repos:
                if i.git_dir not in data:
                    data[i.git_dir] = sha(i.commit())
                    tracked = i.commit()
                    ddump()
                else:
                    tracked = i.commit(data[i.git_dir])

                i.remote().pull()

                if data[i.git_dir] != sha(i.commit()):
                    for j in i.iter_commits(since=tracked.committed_date + 1):
                        mess(i, j)
                    data[i.git_dir] = sha(i.commit())
                    ddump()

            print(f"Next check will occur on {datetime.now() + timedelta(seconds=120)}")
            sleep(30)
    except KeyError:
        print("Waiting for telegram to exit...")
