# Internal helpers and definitions
import h_folder_nav_helpers as fh
import h_FOLDER_DEFINITIONS as fdef
# folder navigation modules
import os
# audio processing modules
from pydub import AudioSegment
from pydub.effects import normalize
# displaying wav file modules
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile


#---------------------------------------#
# CONSTANT DEFINITIONS
#---------------------------------------#
# path to the mono, 16kHz transformed data folder
SOURCE_FOLDER = fdef.MONO_16KHZ_DATA_FOLDER
# path to the normalised data folder
DEST_FOLDER = fdef.AMP_NORM_DATA_FOLDER
#---------------------------------------#

#---------------------------------------#
# GRAPH DISPLAY OPTIONS
#---------------------------------------#
# the files that are to be graphed
WAVS_TO_SHOW = [1, 2, 3, 4, 5]
# whether to show the graphs of the audio files being normaised
SHOW_NORMALISED_GRAPHS = True
#---------------------------------------#

#---------------------------------------#
# GOBAL VARIABLE TRACKERS
#---------------------------------------#
# a counter to keep track of the number of files transformed
files_transformed = 0
#---------------------------------------#


"""
main function
"""
def main() -> None:
    fh.clean_folder(DEST_FOLDER)
    normalise_amp_of_all_files(SOURCE_FOLDER)


"""
convert the given wav file to have a normalised amplitude ranging from -1 to 1.
And export the converted file to the destination folder. The orginal file 
will remain unchanged.

    file: the path to the wav file
"""
def normalise_amp_of_file(file: str) -> None: 
    # normalise the amplitude of the audio file
    audio = AudioSegment.from_file(file)
    normalized_audio = normalize(audio, headroom=1.0)
    output_path = fh.save_new_wav(file, normalized_audio, 
                                  DEST_FOLDER, generate_output_file_name)

    # update the file count
    global files_transformed
    files_transformed += 1
    print(f"Number of files transformed: {files_transformed}", end='\r')

    # we will display a subset of the converted wav files
    if SHOW_NORMALISED_GRAPHS and files_transformed in WAVS_TO_SHOW:
        fh.display_amp_graph(file, output_path)

"""
Generate the output file path of the normalised output file
Format: "{file_name}_normalised.wav"

    file_name: the name of the original file to be converted
"""
def generate_output_file_name(file_name: str) -> str: 
    return f"{file_name}_normalised.wav"

"""
Convert all the wav files in the given folder (including subfolders)
to have a normalised amplitude ranging from -1 to 1. and export the 
converted files to the destination folder. 
The orginal files will remain unchanged.

    folder: the path to the folder containing the wav files
"""
def normalise_amp_of_all_files(folder: str) -> None:
    # get all the files in the folder 
    # including within subfolders
    all_files = fh.make_path_list(folder)
    # for each of the files, convert it in place
    for file in all_files:
        normalise_amp_of_file(file)

#---------------------------------------#
main()
#---------------------------------------#