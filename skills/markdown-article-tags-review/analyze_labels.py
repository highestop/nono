#!/usr/bin/env python3
"""分析 highestop/nono 仓库中带「稍后阅读」label 的所有 issue 的 label 体系。

用法：
    python3 analyze_labels.py            # 自动调用 gh 拉取数据后分析
    python3 analyze_labels.py <file>     # 从 gh 输出的 JSON 文件读取（用于离线/复算）

输出：
    - 各 label 出现次数
    - 仅出现 1 次的 label
    - 始终共现的 label 对（候选合并）
    - 子集关系（A 出现的所有 issue 都包含 B，候选去重）

不修改任何 label，仅做分析。具体合并/重命名/删除由调用方按报告执行。
"""

import json
import subprocess
import sys
from collections import defaultdict

REPO = "highestop/nono"
BASE_LABEL = "稍后阅读"


def fetch_issues() -> list[dict]:
    result = subprocess.run(
        ["gh", "issue", "list", "--repo", REPO, "--label", BASE_LABEL,
         "--state", "all", "--limit", "500", "--json", "number,title,labels"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def load_issues(arg: str | None) -> list[dict]:
    if arg:
        return json.loads(open(arg).read())
    return fetch_issues()


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    data = load_issues(arg)

    label_to_issues: dict[str, list[int]] = defaultdict(list)
    issue_to_labels: dict[int, list[str]] = {}
    issue_titles: dict[int, str] = {}
    for it in data:
        n = it["number"]
        issue_titles[n] = it.get("title", "")
        labs = sorted(l["name"] for l in it["labels"] if l["name"] != BASE_LABEL)
        issue_to_labels[n] = labs
        for l in labs:
            label_to_issues[l].append(n)

    print(f"issue 总数: {len(data)}")
    print(f"label 总数（不含「{BASE_LABEL}」）: {len(label_to_issues)}")

    print("\n=== 各 label 出现次数（按频次降序）===")
    for l, issues in sorted(label_to_issues.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        print(f"  {l}: {len(issues)}  -> {sorted(issues)}")

    once = sorted(l for l, issues in label_to_issues.items() if len(issues) == 1)
    print(f"\n=== 仅出现 1 次的 label ({len(once)}) ===")
    print(f"  {once}")

    issue_sets = {l: frozenset(issues) for l, issues in label_to_issues.items()}
    labels_sorted = sorted(label_to_issues.keys())

    print("\n=== 始终共现（出现 issue 集合完全相同，仅看 ≥2 次的）===")
    found = False
    for i, a in enumerate(labels_sorted):
        for b in labels_sorted[i + 1:]:
            if issue_sets[a] == issue_sets[b] and len(issue_sets[a]) >= 2:
                print(f"  {a}  ≡  {b}  in {sorted(issue_sets[a])}")
                found = True
    if not found:
        print("  （无）")

    print("\n=== 子集关系（A ⊂ B，且 |A|<|B|）===")
    found = False
    for a in labels_sorted:
        for b in labels_sorted:
            if a == b:
                continue
            sa, sb = issue_sets[a], issue_sets[b]
            if len(sa) < len(sb) and sa.issubset(sb):
                print(f"  {a} ({sorted(sa)}) ⊂ {b} ({sorted(sb)})")
                found = True
    if not found:
        print("  （无）")

    print("\n=== issue → labels 一览 ===")
    for n in sorted(issue_to_labels):
        print(f"  #{n}  [{', '.join(issue_to_labels[n])}]  {issue_titles[n][:50]}")


if __name__ == "__main__":
    main()
