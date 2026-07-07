#!/usr/bin/env python3

import json
import os
import urllib.error
import urllib.request
import uuid
from pathlib import Path


REPOSITORY = os.environ["GITHUB_REPOSITORY"]
REPOSITORY_OWNER = os.environ["GITHUB_REPOSITORY_OWNER"].lower()
DOCKER_USERNAME = os.environ["DOCKER_USERNAME"]

REPO_ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = (
    REPO_ROOT
    / "blueos-extension-repository"
    / "repos"
    / REPOSITORY_OWNER
    / "ping-viewer-next-discovery-tweak"
    / "metadata.json"
)
OUTPUT_DIR = Path("/tmp/blueos-manifest")


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def fetch_text(url: str) -> str | None:
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError:
        return None


def docker_tags(docker_repo: str) -> list[dict]:
    namespace, repo = docker_repo.split("/", 1)
    url = f"https://hub.docker.com/v2/namespaces/{namespace}/repositories/{repo}/tags?page_size=100"
    tags: list[dict] = []

    while url:
        response = fetch_json(url)
        tags.extend(response.get("results", []))
        url = response.get("next")

    return tags


def readme_text(metadata: dict, tag_name: str) -> str:
    branch_name = metadata["branch_name"]
    readme_path = metadata["readme_path"]

    if tag_name == branch_name:
        candidates = [
            f"https://raw.githubusercontent.com/{REPOSITORY}/{branch_name}/{readme_path}",
        ]
    else:
        candidates = [
            f"https://raw.githubusercontent.com/{REPOSITORY}/{tag_name}/{readme_path}",
            f"https://raw.githubusercontent.com/{REPOSITORY}/{branch_name}/{readme_path}",
        ]

    for candidate in candidates:
        content = fetch_text(candidate)
        if content:
            return content

    return "No README available"


def version_entry(metadata: dict, docker_tag: dict) -> dict | None:
    images = []

    for image in docker_tag.get("images", []):
        architecture = image.get("architecture")
        os_name = image.get("os")

        if architecture == "unknown" or os_name == "unknown":
            continue

        images.append(
            {
                "expanded_size": image["size"],
                "platform": {
                    "architecture": architecture,
                    "variant": image.get("variant"),
                    "os": os_name,
                },
                "digest": image["digest"],
            }
        )

    if not images:
        return None

    tag_name = docker_tag["name"]

    return {
        "identifier": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{metadata['identifier']}:{tag_name}")),
        "type": metadata["type"],
        "website": None,
        "images": images,
        "authors": metadata["authors"],
        "filter_tags": metadata["filter_tags"],
        "extra_links": metadata["extra_links"],
        "tag": tag_name,
        "docs": metadata["docs"],
        "readme": readme_text(metadata, tag_name),
        "support": metadata["support"],
        "requirements": metadata["requirements"],
        "company": metadata["company"],
        "permissions": metadata["permissions"],
    }


def build_manifest() -> list[dict]:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    docker_repo = f"{DOCKER_USERNAME}/blueos-{metadata['docker_image_name']}"
    base_url = (
        f"https://raw.githubusercontent.com/{REPOSITORY}/gh-pages/"
        f"repos/{REPOSITORY_OWNER}/ping-viewer-next-discovery-tweak"
    )
    company_logo_url = (
        f"https://raw.githubusercontent.com/{REPOSITORY}/gh-pages/"
        f"repos/{REPOSITORY_OWNER}/company_logo.png"
    )

    versions = {}
    tag_results = docker_tags(docker_repo)

    for tag in tag_results:
        entry = version_entry(metadata, tag)
        if entry is not None:
            versions[tag["name"]] = entry

    manifest_entry = {
        "identifier": metadata["identifier"],
        "name": metadata["name"],
        "website": metadata["website"],
        "docker": docker_repo,
        "description": metadata["description"],
        "extension_logo": f"{base_url}/extension_logo.png",
        "company_logo": company_logo_url,
        "versions": versions,
    }

    if tag_results:
        timestamps = [tag["last_updated"] for tag in tag_results if tag.get("last_updated")]
        if timestamps:
            manifest_entry["repo_info"] = {
                "downloads": 0,
                "last_updated": max(timestamps),
                "date_registered": min(timestamps),
            }

    return [manifest_entry]


def main() -> None:
    manifest = build_manifest()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
