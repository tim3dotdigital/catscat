# Internal helpers and definitions
import h_folder_nav_helpers as fh
import h_FOLDER_DEFINITIONS as fdef
# folder navigation modules
import os
# audio processing modules
from pydub import AudioSegment
import librosa
# displaying wav file modules
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.io import wavfile

#---------------------------------------#
# CONSTANT DEFINITIONS
#---------------------------------------#
# path to the amp normalised data folder (source)
SOURCE_FOLDER = fdef.AMP_NORM_DATA_FOLDER
# path to the cetered and trimed data folder (destination)
DEST_FOLDER = fdef.TARGETED_1_2S_DATA_FOLDER
# the categories that we want to ignore when preforming this process
# we normaly wish to ignore the "scratch" sounds as we can process them later
# in f4_1 as they normally require a second pass (see documentation)
IGNORE_CATEGORIES = ["soft-scratch", "hard-scratch", "board-scratch", "pole-scratch"]
# if we wish to first clean out the destionation folder
CLEAN_DEST = False
#---------------------------------------#

#---------------------------------------#
# GRAPH DISPLAY OPTIONS
#---------------------------------------#
# the files that are to be graphed
WAVS_TO_SHOW = [1, 2, 3, 4, 5, 6, 7, 8]
# whether to show the graphs of the audio files being normaised
SHOW_SHIFTED_GRAPHS = True
#---------------------------------------#

#---------------------------------------#
# GOBAL VARIABLE TRACKERS
#---------------------------------------#
files_transformed = 0
#---------------------------------------#



"""
main function
"""
def main() -> None:
    if CLEAN_DEST:
        fh.clean_folder(DEST_FOLDER)
    locate_export_all_target_sections(SOURCE_FOLDER)

"""
locate the target section of the given file
i.e. the audio of interest (e.g. meow)
And then export this section within a 1-2s audio clip

    file: the path to the wav file
"""
def locate_export_target_section(file: str) -> None:
    # Load the WAV file using PyDub
    audio_file = AudioSegment.from_wav(file)

    # Convert the audio into a NumPy array
    audio_array = np.array(audio_file.get_array_of_samples()) / fdef.MAX_16BIT_AMP
    # Find the indices where the audio exceeds 0.5 amplitude
    exceeding_indices = np.where(np.abs(audio_array) > 0.5)[0]
    # if there is no audio of interest then we skip this file
    if len(exceeding_indices) == 0:
        print(f"File {file} has no audio exceeding 0.5 amplitude")
        return

    # Calculate the time at which the audio first exceeds 0.5 amplitude
    first_exceeding_time = exceeding_indices[0] / audio_file.frame_rate
    # Calculate the time at which the audio last exceeds 0.5 amplitude
    last_exceeding_time = exceeding_indices[-1] / audio_file.frame_rate

    # find the time at which the target section starts and ends accounting for lead in
    target_start = max(0, first_exceeding_time - fdef.LEAD_IN_TIME)
    target_end = min(last_exceeding_time + fdef.LEAD_IN_TIME, audio_file.duration_seconds)

    # extract and export only the target section
    target_audio = audio_file[target_start * 1000 : target_end * 1000]  
    output_path = extract_export_target_audio(target_audio, file)

    # update the file count
    global files_transformed
    files_transformed += 1
    print(f"Number of files transformed: {files_transformed}", end='\r')

    # we will display a subset of the converted wav files
    if SHOW_SHIFTED_GRAPHS and files_transformed in WAVS_TO_SHOW:
        # plot the target section, compare the old and new file
        fh.compare_extracted_target_graph(file, output_path, first_exceeding_time, last_exceeding_time)

"""
extract and export the target section of the given audio file and add padding / trim
if needed to ensure that it lies within the 1-2s range.
If the target section is too long we cut the ends.
If the target section is too short we add padding.

    target_audio: the target section of the audio file
    file: the path to the original wav file

    returns: the path to the exported wav file
"""
def extract_export_target_audio(target_audio, file):
    current_duration = target_audio.duration_seconds

    # if the target secion is too long we cut the ends   
    if current_duration > fdef.MAX_LENGTH_S:
        cut_start = int((current_duration - fdef.MAX_LENGTH_S) * 500)
        cut_end = int((current_duration - fdef.MAX_LENGTH_S) * 500)
        target_audio = target_audio[cut_start:-cut_end]

    # if the target secion is too short we add padding
    elif current_duration < fdef.MIN_LENGTH_S:
        padding_duration = fdef.MIN_LENGTH_S - current_duration
        padding_start = int(padding_duration * 500)  # Half of the padding duration in milliseconds
        padding_end = int(padding_duration * 500)
        # add the padding 
        padded_audio = AudioSegment.silent(padding_start) + target_audio + AudioSegment.silent(padding_end)
        target_audio = padded_audio[:fdef.MIN_LENGTH_S * 1000]  # Truncate to the exact target duration

    # export the file
    output_path = fh.save_new_wav(file, target_audio, 
                            DEST_FOLDER, generate_output_file_name)
    return output_path
    
"""
Generate the output file path
Format: "{file_name}_centered_1-2s.wav"

    file_name: the name of the original file
"""
def generate_output_file_name(file_name): 
    return f"{file_name}_centered_1-2s.wav"

"""
Plot audio file highlighting the target section of the given audio file
and the lead in time.

    audio_array: the audio array of the orginal audio file
    first_exceeding_time: the time at which the audio first exceeds 0.5 amplitude
    last_exceeding_time: the time at which the audio last exceeds 0.5 amplitude
    audio_file: the orginal audio file
    file: the path to the original wav file
"""
def plot_target_section(audio_array, first_exceeding_time, last_exceeding_time, audio_file, file):
    time = np.arange(len(audio_array)) / audio_file.frame_rate
    plt.plot(time, audio_array, color='lightskyblue')

    # Highlight the exceeding section
    # Find the indices within the specified range
    target_indices = np.where((time >= first_exceeding_time) & (time <= last_exceeding_time))[0]
    target_leadin_indices = np.where((time >= first_exceeding_time - fdef.LEAD_IN_TIME) 
                                     & (time <= last_exceeding_time + fdef.LEAD_IN_TIME))[0]

    # Highlight the lead in time
    plt.plot(time[target_leadin_indices], audio_array[target_leadin_indices], color='pink')

    # Highlight the points within the specified range in red
    plt.plot(time[target_indices], audio_array[target_indices], color='lightcoral')
    # Set labels and title for the graph
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    file_name = "_".join(os.path.basename(file).split("_")[:3])
    plt.title(file_name)
    plt.grid(True)
    # Show the graph
    plt.show()

"""
locate the target section of the files within the given folder
i.e. the audio of interest (e.g. meow)
And then export this section within a 1-2s audio clip

    folder: the path to the folder containing the wav files
"""
def locate_export_all_target_sections(folder: str) -> None:
    # get all the files in the folder 
    # including within subfolders
    all_files = fh.make_path_list(folder)
    # for each of the files
    for file in all_files:
        if fh.get_category(file) not in IGNORE_CATEGORIES:
            locate_export_target_section(file)



#---------------------------------------#
main()
#---------------------------------------#