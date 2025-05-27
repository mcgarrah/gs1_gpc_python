"""
GPC data downloading functionality.

This module provides functions for downloading GS1 GPC data from the GS1 API
and finding the latest cached XML files.
"""

import os
import logging
import asyncio
from pathlib import Path
from datetime import datetime

# Default paths
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GPC_DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, 'data', 'imports')
DEFAULT_FALLBACK_XML_FILE = os.path.join(GPC_DOWNLOAD_DIR, 'en-v20241202.xml')

# Check if gpcc is available
try:
    import gpcc
    from gpcc._crawlers import fetch_file, get_language, get_publications
    HAS_GPCC = True
except ImportError:
    logging.warning("gpcc library not found. Will use local cached GPC data.")
    HAS_GPCC = False


def find_latest_xml_file(directory=GPC_DOWNLOAD_DIR, language_code='en'):
    """
    Find the latest GPC XML file in the specified directory.
    
    Args:
        directory (str): Directory to search for XML files
        language_code (str): Language code to filter files
        
    Returns:
        str: Path to the latest XML file or None if no files found
    """
    try:
        if not os.path.exists(directory):
            logging.warning("Directory %s does not exist", directory)
            return None
            
        # Get all XML files in the directory
        xml_files = []
        for file in os.listdir(directory):
            # Match both {language_code}-v*.xml and {language_code}-*.xml patterns
            if file.endswith('.xml') and file.startswith(f"{language_code}-"):
                xml_files.append(file)
                
        if not xml_files:
            logging.warning("No XML files found for language '%s' in %s", language_code, directory)
            return None
            
        # Sort files by version (extract version from filename)
        def extract_version(filename):
            # Try to extract version from {language_code}-v{version}.xml format
            if '-v' in filename:
                version = filename.split('-v')[1].split('.')[0]
            # Try to extract version from {language_code}-{version}.xml format
            else:
                version = filename.split('-')[1].split('.')[0]
            return version
            
        # Sort files by version in descending order (newest first)
        xml_files.sort(key=extract_version, reverse=True)
        
        # Return the path to the latest file
        latest_file = os.path.join(directory, xml_files[0])
        logging.info("Found latest XML file: %s", latest_file)
        return latest_file
        
    except Exception as e:
        logging.error("Error finding latest XML file: %s", e)
        return None


async def _download_gpc_xml(output_dir, language_code='en'):
    """
    Download the latest GS1 GPC data in XML format using the gpcc library.
    
    Args:
        output_dir: Directory where the XML file will be saved
        language_code: Language code to download
        
    Returns:
        str: Path to the downloaded file or None if failed
    """
    try:
        # Get language
        lang = await get_language(language_code)
        if not lang:
            logging.error("Could not find language '%s' in GPC API", language_code)
            return None
            
        # Get latest publication for the language
        publications = await get_publications(lang)
        if not publications:
            logging.error("No publications found for language '%s'", language_code)
            return None
            
        # Get the latest publication
        publication = publications[0]
        version = publication.version
        logging.info("Found latest GPC publication: version %s", version)
        
        # Create filename using GPCC standard naming convention
        filename = f"{language_code}-{version}.xml"
        output_path = os.path.join(output_dir, filename)
        
        # Download the XML file
        with open(output_path, 'wb') as stream:
            await fetch_file(stream, publication, format='xml')
            
        return output_path
    except Exception as e:
        logging.error("Error during GPC download: %s", e)
        return None


def download_latest_gpc_xml(language_code='en'):
    """
    Download the latest GS1 GPC data in XML format.
    
    Args:
        language_code: Language code to download
    
    Returns:
        str: Path to the XML file to use for import
    """
    if not HAS_GPCC:
        logging.warning("gpcc library not available. Using local cached version.")
        # Find the latest cached XML file
        cached_file = find_latest_xml_file(GPC_DOWNLOAD_DIR, language_code)
        if cached_file:
            return cached_file
        else:
            logging.warning("No cached XML files found for language '%s'. Using fallback file.", language_code)
            return DEFAULT_FALLBACK_XML_FILE
    
    try:
        logging.info("Attempting to download latest GPC data for language '%s' using gpcc...", language_code)
        
        # Ensure download directory exists
        os.makedirs(GPC_DOWNLOAD_DIR, exist_ok=True)
        
        # Run the async download function
        download_path = asyncio.run(_download_gpc_xml(GPC_DOWNLOAD_DIR, language_code))
        
        if download_path and os.path.exists(download_path):
            logging.info("Successfully downloaded latest GPC data to %s", download_path)
            return download_path
        else:
            logging.warning("Failed to download latest GPC data. Using local cached version.")
            # Find the latest cached XML file
            cached_file = find_latest_xml_file(GPC_DOWNLOAD_DIR, language_code)
            if cached_file:
                return cached_file
            else:
                logging.warning("No cached XML files found for language '%s'. Using fallback file.", language_code)
                return DEFAULT_FALLBACK_XML_FILE
            
    except Exception as e:
        logging.error("Error downloading GPC data: %s", e)
        logging.warning("Falling back to local cached version.")
        # Find the latest cached XML file
        cached_file = find_latest_xml_file(GPC_DOWNLOAD_DIR, language_code)
        if cached_file:
            return cached_file
        else:
            logging.warning("No cached XML files found for language '%s'. Using fallback file.", language_code)
            return DEFAULT_FALLBACK_XML_FILE