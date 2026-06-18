#!/usr/bin/env python3
"""
Kodi repository builder for the Alqatrony repository.

Produces a standards-compliant repo layout that Kodi can install from and
auto-update against:

    kodi-repo/
      repository.alqatrony/                 (repo addon source)
      build_repo.py                          (this script)
      index.html                             (bootstrap download link)
      repository.alqatrony-<ver>.zip         (bootstrap install zip)
      zips/
        addons.xml                           (lists ALL addons)
        addons.xml.md5
        repository.alqatrony/
          repository.alqatrony-<ver>.zip
        service.subtitles.subdlbridge/
          service.subtitles.subdlbridge-<ver>.zip

To publish an update: bump the addon's <version> in its addon.xml, run this
script, then commit & push the kodi-repo repository. Kodi clients pick up the
new version automatically.
"""

import os
import shutil
import zipfile
import hashlib
import xml.etree.ElementTree as ET

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(ROOT_DIR)
ZIPS_DIR = os.path.join(ROOT_DIR, "zips")

REPOSITORY_ID = "repository.alqatrony"

# Addon source folders to include in the repository.
# The repository addon lives inside kodi-repo; the subtitle addon is the
# canonical source kept at the project root (single source of truth).
ADDON_SOURCES = [
    os.path.join(ROOT_DIR, "repository.alqatrony"),
    os.path.join(PROJECT_DIR, "service.subtitles.subdlbridge"),
]

EXCLUDE_DIRS = {".git", ".github", ".idea", "__pycache__"}
EXCLUDE_FILES = {".gitignore", ".gitattributes", ".DS_Store"}
EXCLUDE_EXTS = {".pyc", ".zip"}


def read_addon(source_dir):
    addon_xml = os.path.join(source_dir, "addon.xml")
    if not os.path.isfile(addon_xml):
        print(f"  ! Skipping {source_dir}: no addon.xml")
        return None
    tree = ET.parse(addon_xml)
    root = tree.getroot()
    addon_id = root.get("id")
    version = root.get("version")
    if not addon_id or not version:
        print(f"  ! Skipping {addon_xml}: missing id/version")
        return None
    return {
        "id": addon_id,
        "version": version,
        "path": source_dir,
        "element": root,
    }


def should_include(filename):
    if filename in EXCLUDE_FILES:
        return False
    _, ext = os.path.splitext(filename)
    return ext.lower() not in EXCLUDE_EXTS


def make_zip(addon, dest_zip):
    os.makedirs(os.path.dirname(dest_zip), exist_ok=True)
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for current, dirs, files in os.walk(addon["path"]):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in files:
                if not should_include(f):
                    continue
                abs_path = os.path.join(current, f)
                rel = os.path.relpath(abs_path, addon["path"])
                # Kodi requires the zip's top folder to equal the addon id.
                arcname = os.path.join(addon["id"], rel)
                zf.write(abs_path, arcname)


def main():
    print("Building Alqatrony Kodi repository...\n")

    addons = []
    for src in ADDON_SOURCES:
        info = read_addon(src)
        if info:
            addons.append(info)
            print(f"  + {info['id']} v{info['version']}")

    if not addons:
        print("No addons found. Aborting.")
        return

    # Fresh zips directory
    if os.path.isdir(ZIPS_DIR):
        shutil.rmtree(ZIPS_DIR)
    os.makedirs(ZIPS_DIR)

    print("\nCreating addon zips...")
    for addon in addons:
        zip_name = f"{addon['id']}-{addon['version']}.zip"
        dest = os.path.join(ZIPS_DIR, addon["id"], zip_name)
        make_zip(addon, dest)
        print(f"  - zips/{addon['id']}/{zip_name}")

        # Copy a bootstrap copy of the repository zip to the repo root so users
        # can download & "install from zip" the first time.
        if addon["id"] == REPOSITORY_ID:
            shutil.copy2(dest, os.path.join(ROOT_DIR, zip_name))

    # Build the single addons.xml that lists every addon.
    print("\nGenerating zips/addons.xml ...")
    addons_root = ET.Element("addons")
    for addon in addons:
        addons_root.append(addon["element"])
    ET.indent(addons_root, space="    ")
    xml_bytes = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + \
        ET.tostring(addons_root, encoding="utf-8")

    addons_xml_path = os.path.join(ZIPS_DIR, "addons.xml")
    with open(addons_xml_path, "wb") as f:
        f.write(xml_bytes)

    md5 = hashlib.md5(xml_bytes).hexdigest()
    with open(addons_xml_path + ".md5", "w") as f:
        f.write(md5)
    print("  - zips/addons.xml + zips/addons.xml.md5")

    # Refresh the bootstrap index.html
    repo_version = next(a["version"] for a in addons if a["id"] == REPOSITORY_ID)
    index_html = (
        "<!DOCTYPE html>\n"
        f'<a href="repository.alqatrony-{repo_version}.zip">'
        f"repository.alqatrony-{repo_version}.zip</a>\n"
    )
    with open(os.path.join(ROOT_DIR, "index.html"), "w") as f:
        f.write(index_html)

    print("\nDone. Commit & push the kodi-repo repository to publish.")


if __name__ == "__main__":
    main()
