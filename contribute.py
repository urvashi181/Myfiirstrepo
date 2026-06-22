#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
from datetime import datetime, timedelta
from random import randint


def run(command, env=None):
    subprocess.run(command, check=True, env=env)


def message(date):
    return date.strftime("Contribution: %Y-%m-%d %H:%M")


def contributions_per_day(max_commits):
    max_commits = max(1, min(max_commits, 20))
    return randint(1, max_commits)


def contribute(commit_date):
    with open("README.md", "a", encoding="utf-8") as file:
        file.write(message(commit_date) + "\n\n")

    run(["git", "add", "."])

    env = os.environ.copy()
    git_date = commit_date.strftime("%Y-%m-%d %H:%M:%S")

    env["GIT_AUTHOR_DATE"] = git_date
    env["GIT_COMMITTER_DATE"] = git_date

    run(
        [
            "git",
            "commit",
            "-m",
            message(commit_date)
        ],
        env=env,
    )


def arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-nw",
        "--no_weekends",
        action="store_true",
        help="Do not create commits on weekends"
    )

    parser.add_argument(
        "-mc",
        "--max_commits",
        type=int,
        default=10,
        help="Maximum commits per day (1-20)"
    )

    parser.add_argument(
        "-fr",
        "--frequency",
        type=int,
        default=80,
        help="Percentage chance a day gets commits"
    )

    parser.add_argument(
        "-r",
        "--repository",
        type=str,
        help="GitHub repository URL"
    )

    parser.add_argument(
        "-un",
        "--user_name",
        type=str,
        help="Git user name"
    )

    parser.add_argument(
        "-ue",
        "--user_email",
        type=str,
        help="Git user email"
    )

    parser.add_argument(
        "-db",
        "--days_before",
        type=int,
        default=365,
        help="Days before today"
    )

    parser.add_argument(
        "-da",
        "--days_after",
        type=int,
        default=0,
        help="Days after today"
    )

    return parser.parse_args()


def main():
    args = arguments()

    if args.days_before < 0:
        sys.exit("days_before must be >= 0")

    if args.days_after < 0:
        sys.exit("days_after must be >= 0")

    current_date = datetime.now()

    directory = (
        f"repository-{current_date.strftime('%Y-%m-%d-%H-%M-%S')}"
    )

    if args.repository:
        repo_name = args.repository.split("/")[-1]
        directory = repo_name.replace(".git", "")

    os.mkdir(directory)
    os.chdir(directory)

    try:
        run(["git", "push", "-u", "origin", "main"])
    except subprocess.CalledProcessError:
        print("Push failed. Remote repository already contains commits.")
        print("Run: git pull origin main --allow-unrelated-histories")

    if args.user_name:
        run(["git", "config", "user.name", args.user_name])

    if args.user_email:
        run(["git", "config", "user.email", args.user_email])

    start_date = current_date - timedelta(days=args.days_before)

    total_days = args.days_before + args.days_after + 1

    for day_offset in range(total_days):
        day = start_date + timedelta(days=day_offset)

        if args.no_weekends and day.weekday() >= 5:
            continue

        if randint(1, 100) > args.frequency:
            continue

        commit_count = contributions_per_day(args.max_commits)

        for commit_num in range(commit_count):
            commit_time = day + timedelta(minutes=commit_num)
            contribute(commit_time)

    if args.repository:
        run(["git", "remote", "add", "origin", args.repository])
        run(["git", "branch", "-M", "main"])
        run(["git", "push", "-u", "origin", "main"])

    print("\nRepository generation completed successfully!")


if __name__ == "__main__":
    main()