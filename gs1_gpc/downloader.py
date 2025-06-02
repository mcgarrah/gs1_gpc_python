"""
GPC data downloading functionality.

This module provides classes for downloading GS1 GPC data from the GS1 API
and finding the latest cached XML files.

The main class is GPCDownloader which handles downloading and locating GPC XML files.
Legacy functions are provided for backward compatibility but new code should use
the GPCDownloader class.
"""

import os
import logging
import asyncio
from pathlib import Path
from datetime import datetime

# Default paths
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Default download directory within the library
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


class GPCDownloader:
    """
    Class for downloading and managing GS1 GPC data files.
    
    This class provides methods to download the latest GPC data from the GS1 API
    and find the latest cached XML files in a specified directory. It handles
    fallback mechanisms when downloads fail or when the gpcc library is not available.
    """
    
    def __init__(self, download_dir=None, language_code='en'):
        """
        Initialize a GPCDownloader.
        
        Args:
            download_dir (str, optional): Directory where GPC files will be stored.
                                         If None, uses the default GPC_DOWNLOAD_DIR.
            language_code (str): Language code for GPC data (default: 'en')
        """
        self.download_dir = download_dir if download_dir is not None else GPC_DOWNLOAD_DIR
        self.language_code = language_code
        self.fallback_file = DEFAULT_FALLBACK_XML_FILE
    
    def find_latest_xml_file(self):
        """
        Find the latest GPC XML file in the download directory.
        
        This method searches for XML files matching the pattern {language_code}-*.xml
        and returns the path to the file with the most recent version number.
        The version is extracted from the filename, which can be in either format:
        {language_code}-v{version}.xml or {language_code}-{version}.xml
        
        Returns:
            str: Path to the latest XML file or None if no files found
        """
        try:
            if not os.path.exists(self.download_dir):
                logging.warning("Directory %s does not exist", self.download_dir)
                return None
                
            # Get all XML files in the directory
            xml_files = []
            for file in os.listdir(self.download_dir):
                # Match both {language_code}-v*.xml and {language_code}-*.xml patterns
                if file.endswith('.xml') and file.startswith(f"{self.language_code}-"):
                    xml_files.append(file)
                    
            if not xml_files:
                logging.warning("No XML files found for language '%s' in %s", 
                               self.language_code, self.download_dir)
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
            latest_file = os.path.join(self.download_dir, xml_files[0])
            logging.info("Found latest XML file: %s", latest_file)
            return latest_file
            
        except Exception as e:
            logging.error("Error finding latest XML file: %s", e)
            return None

    async def _download_gpc_xml(self):
        """
        Download the latest GS1 GPC data in XML format using the gpcc library.
        
        Returns:
            str: Path to the downloaded file or None if failed
        """
        try:
            # Get language
            lang = await get_language(self.language_code)
            if not lang:
                logging.error("Could not find language '%s' in GPC API", self.language_code)
                return None
                
            # Get latest publication for the language
            publications = await get_publications(lang)
            if not publications:
                logging.error("No publications found for language '%s'", self.language_code)
                return None
                
            # Get the latest publication
            publication = publications[0]
            version = publication.version
            logging.info("Found latest GPC publication: version %s", version)
            
            # Create filename using GPCC standard naming convention
            filename = f"{self.language_code}-{version}.xml"
            output_path = os.path.join(self.download_dir, filename)
            
            # Download the XML file
            with open(output_path, 'wb') as stream:
                await fetch_file(stream, publication, format='xml')
                
            return output_path
        except Exception as e:
            logging.error("Error during GPC download: %s", e)
            return None

    def download_latest_gpc_xml(self):
        """
        Download the latest GS1 GPC data in XML format.
        
        This method attempts to download the latest GPC data using the gpcc library.
        If the download fails or if gpcc is not available, it falls back to using
        cached XML files. If no cached files are found, it uses the default fallback file.
        
        The downloaded file is saved in the download directory with the naming convention:
        {language_code}-{version}.xml
        
        Returns:
            str: Path to the XML file to use for import (either downloaded or cached)
        """
        if not HAS_GPCC:
            logging.warning("gpcc library not available. Using local cached version.")
            # Find the latest cached XML file
            cached_file = self.find_latest_xml_file()
            if cached_file:
                return cached_file
            else:
                logging.warning("No cached XML files found for language '%s'. Using fallback file.", 
                               self.language_code)
                return self.fallback_file
        
        try:
            logging.info("Attempting to download latest GPC data for language '%s' using gpcc...", 
                        self.language_code)
            
            # Ensure download directory exists
            os.makedirs(self.download_dir, exist_ok=True)
            
            # Run the async download function
            download_path = asyncio.run(self._download_gpc_xml())
            
            if download_path and os.path.exists(download_path):
                logging.info("Successfully downloaded latest GPC data to %s", download_path)
                return download_path
            else:
                logging.warning("Failed to download latest GPC data. Using local cached version.")
                # Find the latest cached XML file
                cached_file = self.find_latest_xml_file()
                if cached_file:
                    return cached_file
                else:
                    logging.warning("No cached XML files found for language '%s'. Using fallback file.", 
                                   self.language_code)
                    return self.fallback_file
                
        except Exception as e:
            logging.error("Error downloading GPC data: %s", e)
            logging.warning("Falling back to local cached version.")
            # Find the latest cached XML file
            cached_file = self.find_latest_xml_file()
            if cached_file:
                return cached_file
            else:
                logging.warning("No cached XML files found for language '%s'. Using fallback file.", 
                               self.language_code)
                return self.fallback_file


# Legacy functions for backward compatibility
def find_latest_xml_file(directory=GPC_DOWNLOAD_DIR, language_code='en'):
    """
    Find the latest GPC XML file in the specified directory.
    
    This is a legacy function maintained for backward compatibility.
    New code should use the GPCDownloader class instead.
    
    Args:
        directory (str): Directory to search for XML files
        language_code (str): Language code to filter files
        
    Returns:
        str: Path to the latest XML file or None if no files found
    """
    downloader = GPCDownloader(download_dir=directory, language_code=language_code)
    return downloader.find_latest_xml_file()


def download_latest_gpc_xml(language_code='en', target_directory=None):
    """
    Download the latest GS1 GPC data in XML format.
    
    This is a legacy function maintained for backward compatibility.
    New code should use the GPCDownloader class instead.
    
    Args:
        language_code: Language code to download
        target_directory: Optional directory where the XML file will be saved.
                         If None, uses GPC_DOWNLOAD_DIR.
    
    Returns:
        str: Path to the XML file to use for import
    """
    downloader = GPCDownloader(download_dir=target_directory, language_code=language_code)
    return downloader.download_latest_gpc_xml()