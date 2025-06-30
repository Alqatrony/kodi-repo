#!/usr/bin/env python3
"""
Repository Generator script for Kodi addons
This script creates:
- zip files of addons
- a root addons.xml for the repository itself
- a zips/addons.xml for installable addons
- corresponding .md5 checksum files
"""

import os
import shutil
import zipfile
import hashlib
import xml.etree.ElementTree as ET
from xml.dom import minidom


class KodiRepositoryGenerator:
    def __init__(self):
        # Assuming the script is in the root of the kodi-repo directory
        self.root_dir = os.path.abspath(os.path.dirname(__file__))
        self.zips_dir = os.path.join(self.root_dir, "zips")
        
        # The addon ID of the repository itself
        self.repository_id = "repository.alqatrony"

        # Paths for the zips/addons.xml, which lists installable addons
        self.addons_xml_path = os.path.join(self.zips_dir, "addons.xml")
        self.addons_xml_md5_path = os.path.join(self.zips_dir, "addons.xml.md5")

        # Paths for the root addons.xml, which defines the repository
        self.repo_xml_path = os.path.join(self.root_dir, "addons.xml")
        self.repo_xml_md5_path = os.path.join(self.root_dir, "addons.xml.md5")

        # Folders/files to exclude from zips
        self.exclude_dirs = ['.git', '.github', '.idea', '__pycache__']
        self.exclude_files = ['.gitignore', '.gitattributes', 'repository.generator.py', 'README.md']

        # Store addon information
        self.addons = []

    def run(self):
        """Runs the full repository generation process."""
        self.setup_directories()
        self.find_addons()
        self.create_addon_zips()
        self.generate_installable_addons_file()
        self.generate_repo_definition_file()
        print("\nRepository generation finished successfully!")

    def setup_directories(self):
        """Create the zips directory if it doesn't exist."""
        if not os.path.exists(self.zips_dir):
            os.makedirs(self.zips_dir)
            print(f"Created directory: {self.zips_dir}")

    def find_addons(self):
        """Find all addon directories in the root folder."""
        for item in os.listdir(self.root_dir):
            item_path = os.path.join(self.root_dir, item)

            if os.path.isdir(item_path) and item not in self.exclude_dirs and item != "zips":
                addon_xml_path = os.path.join(item_path, "addon.xml")
                if os.path.exists(addon_xml_path):
                    addon_info = self._get_addon_info(item_path, addon_xml_path)
                    if addon_info:
                        self.addons.append(addon_info)

    def _get_addon_info(self, addon_dir, addon_xml_path):
        """Extract addon information from addon.xml."""
        try:
            tree = ET.parse(addon_xml_path)
            root = tree.getroot()
            addon_id = root.get('id')
            addon_version = root.get('version')

            if not addon_id or not addon_version:
                print(f"Warning: {addon_xml_path} is missing id or version attributes.")
                return None

            xml_string = ET.tostring(root, encoding='utf-8').decode('utf-8')

            return {
                'id': addon_id,
                'version': addon_version,
                'path': addon_dir,
                'xml_string': xml_string
            }
        except Exception as e:
            print(f"Error processing {addon_xml_path}: {e}")
            return None

    def create_addon_zips(self):
        """Create zip files for all found addons."""
        print("\nCreating addon zip files...")
        for addon in self.addons:
            addon_id = addon['id']
            addon_version = addon['version']
            addon_path = addon['path']
            addon_name = os.path.basename(addon_path)

            zip_filename = f"{addon_id}-{addon_version}.zip" if addon_id != self.repository_id else f"{addon_id}.zip"
            zip_filepath = os.path.join(self.root_dir if addon_id == self.repository_id else self.zips_dir, zip_filename)

            print(f"Creating zip: {zip_filepath}")
            try:
                with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(addon_path):
                        dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                        for file in files:
                            if file not in self.exclude_files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.join(addon_name, os.path.relpath(file_path, addon_path))
                                zf.write(file_path, arcname)
                print(f"- Successfully created {zip_filename}")
            except Exception as e:
                print(f"- Error creating zip {zip_filepath}: {e}")

    def generate_installable_addons_file(self):
        """Generate the zips/addons.xml file with all installable addon metadata."""
        print(f"\nGenerating {self.addons_xml_path}...")
        addons_to_include = [a for a in self.addons if a['id'] != self.repository_id]
        self._generate_xml_file(self.addons_xml_path, addons_to_include)
        self._generate_md5_file(self.addons_xml_path, self.addons_xml_md5_path)

    def generate_repo_definition_file(self):
        """Generate the root addons.xml file that defines the repository itself."""
        print(f"\nGenerating {self.repo_xml_path}...")
        repo_addon = [a for a in self.addons if a['id'] == self.repository_id]
        self._generate_xml_file(self.repo_xml_path, repo_addon)
        self._generate_md5_file(self.repo_xml_path, self.repo_xml_md5_path)

    def _generate_xml_file(self, path, addons):
        """Helper to generate an XML file from a list of addons."""
        if not addons:
            print(f"- No addons to include in {path}. Skipping.")
            return

        root = ET.Element("addons")
        for addon in addons:
            root.append(ET.fromstring(addon['xml_string']))

        rough_xml = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_xml)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8')

        with open(path, 'wb') as f:
            f.write(pretty_xml)
        print(f"- Generated: {os.path.basename(path)}")

    def _generate_md5_file(self, xml_path, md5_path):
        """Helper to generate an MD5 checksum for a given XML file."""
        if not os.path.exists(xml_path):
            return
        try:
            with open(xml_path, 'rb') as f:
                md5_hash = hashlib.md5(f.read()).hexdigest()
            with open(md5_path, 'w') as f:
                f.write(md5_hash)
            print(f"- Generated: {os.path.basename(md5_path)}")
        except Exception as e:
            print(f"- Error generating MD5 for {xml_path}: {e}")


if __name__ == "__main__":
    generator = KodiRepositoryGenerator()
    generator.run()