"""Prints any evaluation case where the two repeats gave different answers."""
import collections
import json

TIMESTAMP = "20260917_2312"

for version in ("v1", "v2", "v3"):
    data = json.load(open(f"evaluation/results_{version}_{TIMESTAMP}.json"))
    answers = collections.defaultdict(list)
    for run in data["runs"]:
        answers[run["case"]].append(str(run["answer"]))
    for case, pair in answers.items():
        if len(set(pair)) > 1:
            print(f"{version} {case}")
            for answer in pair:
                print(f"    {answer}")
