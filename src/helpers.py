from typing import List
import os
from collections import namedtuple
import io

FilenameInfo = namedtuple("FilenameInfo", ["title", "filename"])
FilenameInfo.__doc__ = """
A named tuple used to return a filename and additional properties, like a title.
"""

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

def get_full_path(relative_path:str) -> str:
	"""
	Returns the absolute path of a file relative to the current file (helpers.py).
	This is useful when debugging, because the current working directory
	is not necessarily the directory of the current file.
	For example, ehen trying to load an image from "assets/fields/field1.png",
	the current working directory is the root directory of the project,
	so the image cannot be found.
	Using instead get_full_path("assets/fields/field1.png") will return
	"/home/username/Projects/foosion/assets/fields/field1.png", which is
	the correct path.

	Parameters:
	relative_path (str): The relative path to a file.

	Returns:
	str: The absolute path of the file.
	"""
	return os.path.join(os.path.dirname(__file__), relative_path)


def get_game_fields() -> List[FilenameInfo]:
	"""
	Returns a list of all available game fields from the assets/fields folder (the full path is returned)
	All JPG, JPEG and PNG files are considered game fields.
	"""
	
	assets_folder = get_full_path("assets/fields")
	filenames = os.listdir(assets_folder)
	filtered_filenames = [filename for filename in filenames if filename.lower().endswith(('.jpg', '.jpeg', '.png'))]
	
	ret = [
		FilenameInfo(
			title=os.path.splitext(full_filename)[0],
			filename=os.path.join(assets_folder, full_filename)
		) for full_filename in filtered_filenames
		]
	
	return ret

def get_sounds(subfolder:str) -> List[FilenameInfo]:
	"""
	Returns a list of all available goal sound FX from the assets/sounds/SUBFOLDER folder (the full path is returned)
	All WAV, OGG, and MP3 files are considered game fields.
	"""
	
	assets_folder = get_full_path(f"assets/sounds/{subfolder}")
	filenames = os.listdir(assets_folder)
	filtered_filenames = [filename for filename in filenames if filename.lower().endswith(('.wav', '.ogg', '.mp3'))]
	
	ret = [
		FilenameInfo(
			title=os.path.splitext(full_filename)[0],
			filename=os.path.join(assets_folder, full_filename)
		) for full_filename in filtered_filenames
		]
	
	return ret