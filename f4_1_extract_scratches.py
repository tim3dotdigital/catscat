"""
Extract the first round of target sounds as normal
Remove those sounds from the files, and re-run the process with the altered files
   - normalise the files
   - extract the target sounds

name as: board-scratch-2ndpass_1_0.wav
"""
# Internal helpers and definitions
import h_folder_nav_helpers as fh
import h_FOLDER_DEFINITIONS as fdef
# folder navigation modules
import os
# audio processing modules
from pydub import AudioSegment
import librosa
from pydub.effects import normalize
# display the wav files amp
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.io import wavfile

#---------------------------------------#
# CONSTANT DEFINITIONS                  #
#---------------------------------------#
# path to the amp normalised data folder (source)
SOURCE_FOLDER = fdef.AMP_NORM_DATA_FOLDER
# path to the cetered and trimed data folder (destination)
DEST_FOLDER = fdef.TARGETED_1_2S_DATA_FOLDER
# the categories that we want to process
# we normaly wish to target the "scratch" sounds as 
# those are the sounds with multiple useful snippets
CATEGORIES_TO_PROCESS = ["soft-scratch", "hard-scratch", "board-scratch", "pole-scratch"]
#---------------------------------------#

#---------------------------------------#
# GRAPH DISPLAY OPTIONS                 #
#---------------------------------------#
# the files that are to be graphed
WAVS_TO_SHOW = [1, 2, 3, 4, 5, 6, 7, 8]
# whether to show the graphs of the audio files being normaised
SHOW_SHIFTED_GRAPHS = True
#---------------------------------------#

#---------------------------------------#
# SECOND PASS OPTIONS                   #
#---------------------------------------#
# addtional tag to add to the end of the file name to signify that it is the 2nd pass
ADDITIONAL_2ND_PASS_TAG = "2ndpass"
# the min file length inorder to preform a second pass
MIN_SECONDS_TO_DO_SECOND_PASS = 1.0
#---------------------------------------#

#---------------------------------------#
# GOBAL VARIABLE TRACKERS               #
#---------------------------------------#
files_transformed = 0
#---------------------------------------#



"""
main function
"""
def main():
    #fh.clean_folder(DEST_FOLDER)
    fh.clean_folder(fdef.TEMP_FOLDER)
    extract_target_all(SOURCE_FOLDER)
    normalise_amp_of_temp_files(fdef.EMP_LEFTOVER_FOLDER, fdef.TEMP_NORMALISED_FOLDER)
    extract_target_all(fdef.TEMP_NORMALISED_FOLDER, ADDITIONAL_2ND_PASS_TAG)



"""
convert all the audio files in the folder to have normalised amplitude
And export the converted files to the temp normalised folder.
"""
def normalise_amp_of_temp_files(left_over_folder, normalised_folder):
    # get all the files in the folder 
    # including within subfolders
    all_files = fh.make_path_list(left_over_folder)
    
    # for each of the files, convert it in place
    for file in all_files:
        normalise_amp_of_file(file, normalised_folder)

"""
convert the given wav file to have a normalised amplitude
ranging from -1 to 1
"""
def normalise_amp_of_file(file, normalised_folder): 
    # normalise the amplitude of the audio file
    audio = AudioSegment.from_file(file)
    normalized_audio = normalize(audio, headroom=1.0)
    output_path = fh.save_new_wav(file, normalized_audio, 
                                  normalised_folder, generate_output_file_name, "do_nothing")

"""
extract the target section of the given file to a new file
"""
def extract_target_file(file, tag=None):
    # Load the WAV file using PyDub
    audio_file = AudioSegment.from_wav(file)

    # Convert the audio into a NumPy array
    audio_array = np.array(audio_file.get_array_of_samples()) / fdef.MAX_16BIT_AMP
    # Find the indices where the audio exceeds 0.5 amplitude
    exceeding_indices = np.where(np.abs(audio_array) > 0.5)[0]

    if len(exceeding_indices) == 0:
        print(f"File {file} has no audio exceeding 0.5 amplitude")
        return

    # Calculate the time at which the audio first exceeds 0.5 amplitude
    first_exceeding_time = exceeding_indices[0] / audio_file.frame_rate
    # Calculate the time at which the audio last exceeds 0.5 amplitude
    last_exceeding_time = exceeding_indices[-1] / audio_file.frame_rate

    target_start = max(0, first_exceeding_time - fdef.LEAD_IN_TIME)
    target_end = min(last_exceeding_time + fdef.LEAD_IN_TIME, audio_file.duration_seconds)

    # extract and export only the target section
    target_audio = audio_file[target_start * 1000 : target_end * 1000]  
    output_path = extract_export_target_audio(target_audio, file, tag)

    # update the file count
    global files_transformed
    files_transformed += 1
    print(f"Number of files transformed: {files_transformed}", end='\r')

    # export the audio with the target section removed
    export_leftover_audio(file, audio_file, target_start, target_end, tag)

    # we will display a subset of the converted wav files
    if SHOW_SHIFTED_GRAPHS and files_transformed in WAVS_TO_SHOW:
        # plot the target section
        # compare the old and new file
        fh.compare_waves_graph(file, output_path, first_exceeding_time, last_exceeding_time)
    
"""
export the left over audio (where the target audio has been removed)
to a new file
"""
def export_leftover_audio(file, audio_file, target_start, target_end, tag):
    # get the leftover sections
    left_audio = audio_file[: target_start* 1000]
    right_audio = audio_file[target_end* 1000 :]
    left_over_audio = left_audio + right_audio

    # export the leftover sections
    if left_over_audio.duration_seconds > MIN_SECONDS_TO_DO_SECOND_PASS:
        output_path = fh.save_new_wav(file, left_over_audio, 
                            fdef.TEMP_LEFTOVER_FOLDER, generate_output_file_name, tag)

"""
export the target audio to a new file
"""
def extract_export_target_audio(target_audio, file, tag=None):
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
        
        padded_audio = AudioSegment.silent(padding_start) + target_audio + AudioSegment.silent(padding_end)
        target_audio = padded_audio[:fdef.MIN_LENGTH_S * 1000]  # Truncate to the exact target duration


    # export the file
    output_path = fh.save_new_wav(file, target_audio, 
                            DEST_FOLDER, generate_output_file_name, tag)
    return output_path

"""
generate the output file path
"""
def generate_output_file_name(file_name, tag=None): 
    if not tag: # board-scratch_1_0_centered_1-2s.wav
        return f"{file_name}_centered_1-2s.wav"
    elif tag == ADDITIONAL_2ND_PASS_TAG: # board-scratch_1_0_centered_1-2s_2ndpass.wav
        return f"{file_name}_{tag}.wav"
    else: # if we do not want to change the file name
        return file_name

"""
center all the files around the "sound of interest"
and trim the files to be 2 seconds long
"""
def extract_target_all(folder, tag=None):
    # get all the files in the folder 
    # including within subfolders
    all_files = fh.make_path_list(folder)
    
    # for each of the files, convert it in place
    for file in all_files:
        if fh.get_category(file) in CATEGORIES_TO_PROCESS:
            extract_target_file(file, tag)



#---------------------------------------#
main()
#---------------------------------------#