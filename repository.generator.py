#!/usr/bin/env python3
"""
Repository Generator script for Kodi addons
This script creates:
- zip files of addons
- addons.xml file with metadata
- addons.xml.md5 checksum file
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
        self.addons_xml_path = os.path.join(self.zips_dir, "addons.xml")
        self.addons_xml_md5_path = os.path.join(self.zips_dir, "addons.xml.md5")
        
        # Folders/files to exclude from zips
        self.exclude_dirs = ['.git', '.github', '.idea', '__pycache__']
        self.exclude_files = ['.gitignore', '.gitattributes', 'repository.generator.py', 'README.md']
        
        # Store addon information
        self.addons = []

    def setup_directories(self):
        """Create the zips directory if it doesn't exist"""
        if not os.path.exists(self.zips_dir):
            os.makedirs(self.zips_dir)
            print(f"Created directory: {self.zips_dir}")

    def find_addons(self):
        """Find all addon directories in both the root folder and zips folder"""
        # Look for addons in the root directory
        for item in os.listdir(self.root_dir):
            item_path = os.path.join(self.root_dir, item)
            
            # Skip if it's not a directory or if it's in the exclude list
            if not os.path.isdir(item_path) or item in self.exclude_dirs or item == "zips":
                continue
                
            # Check if it has an addon.xml (confirming it's a valid addon)
            addon_xml_path = os.path.join(item_path, "addon.xml")
            if os.path.exists(addon_xml_path):
                addon_info = self._get_addon_info(item_path, addon_xml_path)
                if addon_info:
                    self.addons.append(addon_info)
        
        # Look for addons in the zips directory
        if os.path.exists(self.zips_dir):
            for item in os.listdir(self.zips_dir):
                item_path = os.path.join(self.zips_dir, item)
                
                # Skip if it's not a directory or if it's a zip file or xml file
                if not os.path.isdir(item_path):
                    continue
                    
                # Check if it has an addon.xml (confirming it's a valid addon)
                addon_xml_path = os.path.join(item_path, "addon.xml")
                if os.path.exists(addon_xml_path):
                    addon_info = self._get_addon_info(item_path, addon_xml_path, in_zips=True)
                    if addon_info:
                        self.addons.append(addon_info)

    def _get_addon_info(self, addon_dir, addon_xml_path, in_zips=False):
        """Extract addon information from addon.xml"""
        try:
            tree = ET.parse(addon_xml_path)
            root = tree.getroot()
            
            addon_id = root.get('id')
            addon_version = root.get('version')
            
            if not addon_id or not addon_version:
                print(f"Warning: {addon_xml_path} is missing id or version attributes")
                return None
                
            # Get XML string for addons.xml generation
            xml_string = ET.tostring(root, encoding='utf-8').decode('utf-8')
            
            return {
                'id': addon_id,
                'version': addon_version,
                'path': addon_dir,
                'name': os.path.basename(addon_dir),
                'in_zips': in_zips,
                'xml_string': xml_string
            }
        except ET.ParseError as e:
            print(f"Error parsing {addon_xml_path}: {e}")
            return None
        except Exception as e:
            print(f"Error processing {addon_xml_path}: {e}")
            return None

    def create_addon_zips(self):
        """Create zip files for all found addons"""
        for addon in self.addons:
            addon_id = addon['id']
            addon_version = addon['version']
            addon_path = addon['path']
            addon_name = addon['name']
            
            # Path for the zip file
            zip_filename = f"{addon_id}-{addon_version}.zip"
            zip_filepath = os.path.join(self.zips_dir, zip_filename)
            
            # Remove existing zip file if it exists
            if os.path.exists(zip_filepath):
                os.remove(zip_filepath)
                
            print(f"Creating zip: {zip_filepath}")
            try:
                with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zf:
                    # Walk through the addon directory
                    for root, dirs, files in os.walk(addon_path):
                        # Remove excluded directories from processing
                        dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                        
                        # Determine relative path for files within zip
                        # Need different logic based on whether addon is in root or zips dir
                        if addon['in_zips']:
                            rel_root = os.path.relpath(root, addon_path)
                            base_in_zip = addon_name
                        else:
                            rel_root = os.path.relpath(root, self.root_dir)
                        
                        # Add each file to the zip
                        for file in files:
                            if file not in self.exclude_files:
                                file_path = os.path.join(root, file)
                                
                                # Create the path for the file within the zip
                                if addon['in_zips']:
                                    if rel_root == '.':  # If we're in the root of the addon
                                        arcname = os.path.join(base_in_zip, file)
                                    else:
                                        arcname = os.path.join(base_in_zip, rel_root, file)
                                else:
                                    # For addons in the repo root, preserve the folder structure
                                    arcname = rel_root + '/' + file if rel_root != '.' else file
                                
                                zf.write(file_path, arcname)
                
                print(f"Successfully created {zip_filename}")
                
                # Create addon subdirectory in zips if it doesn't exist
                addon_zip_dir = os.path.join(self.zips_dir, addon_name)
                if not os.path.exists(addon_zip_dir) and not addon['in_zips']:
                    os.makedirs(addon_zip_dir)
                
                # Copy addon.xml to the addon's directory in zips if not already there
                if not addon['in_zips']:
                    addon_xml_source = os.path.join(addon_path, "addon.xml")
                    addon_xml_dest = os.path.join(addon_zip_dir, "addon.xml")
                    shutil.copy(addon_xml_source, addon_xml_dest)
                    print(f"Copied addon.xml to: {addon_zip_dir}")
            
            except Exception as e:
                print(f"Error creating zip {zip_filepath}: {e}")
                # Clean up partial zip file if it exists
                if os.path.exists(zip_filepath):
                    os.remove(zip_filepath)

    def generate_addons_xml(self):
        """Generate the addons.xml file with all addon metadata"""
        print(f"Generating {self.addons_xml_path}...")
        
        # Create root element and add XML declaration
        root = ET.Element("addons")
        
        # Add each addon's XML to the master addons.xml
        for addon in self.addons:
            if addon['xml_string']:
                # Parse the XML string into an element
                addon_element = ET.fromstring(addon['xml_string'])
                root.append(addon_element)
        
        # Format the XML nicely
        rough_xml = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_xml)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8')
        
        # Write to file
        with open(self.addons_xml_path, 'wb') as f:
            f.write(pretty_xml)
            
        print(f"Generated: {self.addons_xml_path}")

    def generate_md5_file(self):
        """Generate an MD5 checksum for addons.xml"""
        print(f"Generating {self.addons_xml_md5_path}...")
        
        try:
            # Calculate MD5 in binary mode
            with open(self.addons_xml_path, 'rb') as f:
                content = f.read()
            md5_hash = hashlib.md5(content).hexdigest()
            
            # Write MD5 to file
            with open(self.addons_xml_md5_path, 'w') as f:
                f.write(md5_hash)
                
            print(f"Generated MD5: {self.addons_xml_md5_path} with hash: {md5_hash}")
        except FileNotFoundError:
            print(f"Error: {self.addons_xml_path} not found. Cannot generate MD5 file.")
        except Exception as e:
            print(f"Error generating MD5 file: {e}")

    def run(self):
        """Execute the full repository generation process"""
        print("Starting Kodi repository generation...")
        
        self.setup_directories()
        self.find_addons()
        
        if not self.addons:
            print("No valid addon directories found!")
            return
            
        print(f"Found {len(self.addons)} addons:")
        for addon in self.addons:
            location = "zips directory" if addon['in_zips'] else "root directory"
            print(f"  - {addon['id']} (v{addon['version']}) in {location}")
        
        self.create_addon_zips()
        self.generate_addons_xml()
        self.generate_md5_file()
        
        print("\nRepository generation completed successfully!")


if __name__ == "__main__":
    generator = KodiRepositoryGenerator()
    generator.run()