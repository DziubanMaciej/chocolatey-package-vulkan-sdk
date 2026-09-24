#!/usr/bin/env python3
"""
Checks LunarG Vulkan SDK API for the latest Windows release,
and updates vulkan-sdk.nuspec and tools/chocolateyinstall.ps1 if a new version is found.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

NUSPEC_PATH = os.path.join(os.path.dirname(__file__), "..", "vulkan-sdk.nuspec")
INSTALL_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "tools", "chocolateyinstall.ps1")

HEADERS = {
    "User-Agent": "chocolatey-package-vulkan-sdk-updater/1.0"
}


def get_current_version(nuspec_path: str) -> str:
    with open(nuspec_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"<version>([^<]+)</version>", content)
    if not match:
        raise ValueError("Could not find <version> in nuspec file.")
    return match.group(1).strip()


def get_latest_version() -> str:
    url = "https://vulkan.lunarg.com/sdk/latest/windows.json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            version = data.get("windows")
            if version:
                return version.strip()
    except Exception as e:
        print(f"Warning: Failed to fetch JSON version from {url}: {e}. Trying .txt endpoint...")

    # Fallback to .txt endpoint
    txt_url = "https://vulkan.lunarg.com/sdk/latest/windows.txt"
    req_txt = urllib.request.Request(txt_url, headers=HEADERS)
    with urllib.request.urlopen(req_txt, timeout=30) as resp:
        return resp.read().decode("utf-8").strip()


def get_sha256(version: str) -> str:
    sha_json_url = f"https://sdk.lunarg.com/sdk/sha/{version}/windows/vulkan_sdk.exe.json"
    req = urllib.request.Request(sha_json_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sha = data.get("sha")
            if sha:
                return sha.strip().upper()
    except Exception as e:
        print(f"Notice: Failed to fetch SHA256 JSON from {sha_json_url}: {e}. Trying .txt endpoint...")

    sha_txt_url = f"https://sdk.lunarg.com/sdk/sha/{version}/windows/vulkan_sdk.exe.txt"
    try:
        req_txt = urllib.request.Request(sha_txt_url, headers=HEADERS)
        with urllib.request.urlopen(req_txt, timeout=30) as resp:
            content = resp.read().decode("utf-8").strip()
            # Content is typically: "<sha>  <filename>"
            sha = content.split()[0]
            if len(sha) == 64:
                return sha.upper()
    except Exception as e:
        print(f"Notice: Failed to fetch SHA256 txt from {sha_txt_url}: {e}. Streaming download to calculate SHA256...")

    # Fallback: stream download installer and calculate SHA256
    download_url = f"https://sdk.lunarg.com/sdk/download/{version}/windows/vulkansdk-windows-X64-{version}.exe"
    print(f"Downloading installer from {download_url} to calculate SHA256...")
    req_dl = urllib.request.Request(download_url, headers=HEADERS)
    hasher = hashlib.sha256()
    with urllib.request.urlopen(req_dl, timeout=120) as resp:
        while chunk := resp.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def update_files(nuspec_path: str, install_script_path: str, new_version: str, sha256: str) -> None:
    # Update nuspec
    with open(nuspec_path, "r", encoding="utf-8") as f:
        nuspec_content = f.read()

    new_nuspec = re.sub(
        r"<version>[^<]+</version>",
        f"<version>{new_version}</version>",
        nuspec_content,
        count=1
    )
    with open(nuspec_path, "w", encoding="utf-8") as f:
        f.write(new_nuspec)

    # Update chocolateyinstall.ps1
    with open(install_script_path, "r", encoding="utf-8") as f:
        install_content = f.read()

    new_install = re.sub(
        r'\$sdk_version\s*=\s*"[^"]+"',
        f'$sdk_version = "{new_version}"',
        install_content,
        count=1
    )
    new_install = re.sub(
        r"checksum\s*=\s*'[^']+'",
        f"checksum      = '{sha256}'",
        new_install,
        count=1
    )
    with open(install_script_path, "w", encoding="utf-8") as f:
        f.write(new_install)


def set_github_output(name: str, value: str) -> None:
    output_file = os.getenv("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")


def main():
    parser = argparse.ArgumentParser(description="Check and update Vulkan SDK version.")
    parser.add_argument("--check-only", action="store_true", help="Only check for updates without modifying files.")
    parser.add_argument("--force-version", type=str, help="Force update to a specific version.")
    args = parser.parse_args()

    nuspec_file = os.path.abspath(NUSPEC_PATH)
    install_file = os.path.abspath(INSTALL_SCRIPT_PATH)

    current_version = get_current_version(nuspec_file)
    print(f"Current package version: {current_version}")

    latest_version = args.force_version if args.force_version else get_latest_version()
    print(f"Latest LunarG SDK version: {latest_version}")

    if latest_version == current_version:
        print("Package is already up to date.")
        set_github_output("updated", "false")
        set_github_output("version", latest_version)
        return

    print(f"Update available: {current_version} -> {latest_version}")

    if args.check_only:
        set_github_output("updated", "true")
        set_github_output("version", latest_version)
        set_github_output("old_version", current_version)
        return

    sha256 = get_sha256(latest_version)
    print(f"SHA-256 for {latest_version}: {sha256}")

    update_files(nuspec_file, install_file, latest_version, sha256)
    print(f"Files successfully updated to {latest_version}.")

    set_github_output("updated", "true")
    set_github_output("version", latest_version)
    set_github_output("old_version", current_version)
    set_github_output("sha256", sha256)


if __name__ == "__main__":
    main()
