from git.repo import Repo
from os import mkdir, listdir
from os.path import exists, isdir, join


def exit_empty():
    print("Clone repositories into the \"repos\" to track them")
    exit()


if __name__ == "__main__":
    if not exists("repos"):
        mkdir("repos")
        exit_empty()

    repos = []
    folds = listdir("repos")
    if not folds:
        exit_empty()

    for i in folds:
        repos.append(Repo.init(join("repos", i)))

    for i in repos:
        i.remote().pull()
