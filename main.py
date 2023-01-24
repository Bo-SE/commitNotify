from git.repo import Repo
from git.exc import GitCommandError
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


def mess(repo, commit, branch):
    repo_url = list(repo.remote().urls)[0].replace('.git', '')
    body = f"New commit on " \
           f"**[{escape(repo_url.replace('https://github.com/', ''))}]" \
           f"({escape(repo_url)})** inside branch **{escape(branch)}** " \
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

        for r in folds:
            repos.append(Repo.init(join("repos", r)))

        if not exists("data.json"):
            dump({}, open("data.json", "w+"))
        data = load(open("data.json"))


        def ddump():
            dump(data, open("data.json", "w+"))


        while True:
            for r in repos:
                if r.git_dir not in data:
                    data[r.git_dir] = {}
                else:
                    # backward compatibility conversion
                    if isinstance(data[r.git_dir], str):
                        data[r.git_dir] = {r.active_branch.name: data[r.git_dir]}
                        ddump()
                for b, b_name in map(lambda l: (l, l.name), r.refs):
                    if b_name == "origin/HEAD":
                        continue
                    if "origin/" in str(b_name):
                        b_name = b_name.split("/")[-1]
                    if b != r.active_branch:
                        r.git.checkout(b_name)
                    if b_name not in data[r.git_dir]:
                        data[r.git_dir][b_name] = sha(b.commit)
                        tracked = r.commit()
                        ddump()
                    else:
                        tracked = r.commit(data[r.git_dir][b_name])

                    while True:
                        try:
                            r.remote().pull()
                            break
                        except GitCommandError as e:
                            print("GitCommandError occurred:")
                            print(e)
                        sleep(5)

                    if data[r.git_dir][b_name] != sha(r.commit()):
                        for j in r.iter_commits(since=tracked.committed_date + 1):
                            mess(r, j, b_name)
                        data[r.git_dir][b_name] = sha(r.commit())
                        ddump()

            print(f"Next check will occur on {datetime.now() + timedelta(seconds=120)}")
            sleep(30)
    except KeyboardInterrupt:
        print("Waiting for telegram to exit...")
