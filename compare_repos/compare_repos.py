#!/usr/bin/env python3

import argparse
import subprocess
import os
import sys
import time
import json
import pdb

SKIPPED_FILES = [
    "repository.catalog",
    "maven-metadata.xml",
    "Packages.bz2",
    ".gemspec.rz",
    "Packages.gz",
    "Release",
    ".json",
    "Packages",
    "by-hash",
    "filelists.xml.gz",
    "other.xml.gz",
    "primary.xml.gz",
    "repomd.xml",
    "repomd.xml.asc",
    "repomd.xml.key",
]

SKIPPED_PATTERNS = (
    ".npm",
    ".jfrog",
    ".pypi",
    ".composer",
    "index.yaml",
    "versions",
    "_uploads",
)


def run_jf_aql(server_id, repo):
    # Artifactory AQL has a default limit of 500,000 results per query.
    # To fetch all results, use pagination with "offset" and "limit".
    all_results = {"results": []}
    limit = 100000  # You can adjust this chunk size (max 500,000 per query)
    offset = 0

    while True:
        aql = (
            f'items.find({{"repo": "{repo}"}})'
            f'.include("repo","path","name","sha256")'
            f".offset({offset}).limit({limit})"
        )
        cmd = [
            "jf",
            "rt",
            "curl",
            "-s",
            "-XPOST",
            "-H",
            "Content-Type: text/plain",
            "api/search/aql",
            "--server-id",
            server_id,
            "--data",
            aql,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, check=True, text=True)
            data = json.loads(result.stdout)
            batch = data.get("results", [])
            all_results["results"].extend(batch)
            if len(batch) < limit:
                break  # No more results
            offset += limit
        except subprocess.CalledProcessError as e:
            print(f"Error running jf CLI: {e}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print("Failed to parse JSON output from jf CLI.", file=sys.stderr)
            sys.exit(1)
    return all_results


def get_file_list(results):
    file_list = []
    for item in results.get("results", []):
        path = item.get("path", "")
        name = item.get("name", "")
        sha256 = item.get("sha256", "")
        full_path = f"{path}/{name}" if path else name
        file_list.append((full_path, str(sha256)))
    return file_list


def filter_skipped(files):
    filtered = []
    for path, sha256 in files:
        bname = os.path.basename(path)
        if any(path.startswith(p) for p in SKIPPED_PATTERNS) or bname in SKIPPED_FILES:
            continue
        if "_uploads" in path or "tags.json" in path or "repository_v2.catalog" in path:
            continue
        filtered.append((path, sha256))
    return filtered


def compare_and_log(source_files, target_files, repo, output_dir):
    source_set = set(source_files)
    target_set = set(target_files)
    # Build a set of sha256 values from the target files
    target_sha256_set = set(sha256 for _, sha256 in target_files if sha256)
    # Find files in source whose sha256 is not present in target
    diff = [
        (path, sha256)
        for path, sha256 in source_files
        if sha256 and sha256 not in target_sha256_set
    ]

    filtered_diff = filter_skipped(diff)
    output_file = os.path.join(output_dir, f"{repo}.txt")
    if filtered_diff:
        with open(output_file, "w") as f:
            f.write("-------------------------------------------------\n")
            f.write(f"Files diff from source - Repo [{repo}]\n")
            f.write("-------------------------------------------------\n")
            for idx, (path, sha256) in enumerate(filtered_diff, 1):
                f.write(f"{idx}\t{path},{sha256}\n")
        print(f"\033[1m\033[93mWriting differences to {output_file}\033[0m")
    else:
        print(f"\033[1;92mNo differences found for {repo} after filtering.\033[0m")


def usage():
    print(
        'Usage: python compare_repos.py SOURCE_ID TARGET_ID "REPO1 REPO2 ..."\n'
        "Arguments:\n"
        "  SOURCE_ID   Artifactory server ID for the source (e.g., src-server)\n"
        "  TARGET_ID   Artifactory server ID for the target (e.g., tgt-server)\n"
        '  REPO_LIST   Space-separated list of repository names in quotes (e.g., "repo1 repo2 repo3")\n'
        "\n"
        "Example:\n"
        '  python compare_repos.py src-server tgt-server "repo1 repo2"\n'
    )


def main():
    parser = argparse.ArgumentParser(
        description="Compare repositories between two Artifactory servers."
    )
    parser.add_argument("SOURCE_ID", help="Source Artifactory server ID")
    parser.add_argument("TARGET_ID", help="Target Artifactory server ID")
    parser.add_argument(
        "REPO_MAPPING_FILE", help="Path to JSON file containing repo mapping"
    )

    if len(sys.argv) < 4:
        usage()
        sys.exit(1)
    args = parser.parse_args()

    output_dir = f"out_{int(time.time())}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    print(f"Starting comparison using repo mapping file: {args.REPO_MAPPING_FILE}")

    repo_mapping_list = {}
    with open(args.REPO_MAPPING_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) == 2:
                src_repo, tgt_repo = parts
                repo_mapping_list[src_repo.strip()] = tgt_repo.strip()

    for repo in repo_mapping_list.keys():
        print("-------------------------------------------------")
        print(f"Comparing repository: {repo}")
        print(f"Fetching file list from source ({args.SOURCE_ID})...")
        src_results = run_jf_aql(args.SOURCE_ID, repo)
        src_files = get_file_list(src_results)

        print(f"Fetching file list from target ({args.TARGET_ID})...")
        if repo in repo_mapping_list:
            target_repo = repo_mapping_list[repo]
            print(f"Using mapped repository name: {target_repo}")
        tgt_results = run_jf_aql(args.TARGET_ID, target_repo)
        tgt_files = get_file_list(tgt_results)

        print("Comparing file lists...")
        compare_and_log(src_files, tgt_files, repo, output_dir)
        print(f"Done comparing {target_repo}.")

    print(f"Comparison complete. Check the '{output_dir}' directory for results.")
    print(
        "cat {output_dir}/*.txt | grep -v '_uploads' | grep -v 'tags.json'".format(
            output_dir=output_dir
        )
    )


if __name__ == "__main__":
    main()
