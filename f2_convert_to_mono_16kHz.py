# Internal helpers and definitions
import h_folder_nav_helpers as fh
import h_FOLDER_DEFINITIONS as fdef
# folder navigation modules
import os
# audio processing modules
import wave
from pydub import AudioSegment



#---------------------------------------#
# CONSTANT DEFINITIONS
#---------------------------------------#
# path to the final data
SOURCE_FOLDER = fdef.FINAL_DATA_FOLDER
# path to the mono, 16kHz transformed data folder
DEST_FOLDER = fdef.MONO_16KHZ_DATA_FOLDER
#---------------------------------------#

#---------------------------------------#
# GOBAL VARIABLE TRACKERS
#---------------------------------------#
files_transformed = 0
#---------------------------------------#



"""
main function
"""
def main():
    fh.clean_folder(DEST_FOLDER)
    convert_all_audio_files_mono_16khz(SOURCE_FOLDER)   

"""
Convert the given audio file to mono & 16kHz and export the
converted file to the destination folder. The orginal file 
will remain unchanged

    file: the file to convert
"""
def convert_audio_file_mono_16khz(file: str) -> None:
    # convert all the audio snippits to channel type "Mono" 
    # and convert all the audio snippits to sampling frequency "16kHz"
    # Load the WAV file
    audio = AudioSegment.from_wav(file)  
    # Convert to mono
    audio_mono = audio.set_channels(1)
    # Convert to 16kHz sampling frequency
    audio_mono_16khz = audio_mono.set_frame_rate(16000)

    # Save the transformed audio file
    fh.save_new_wav(file, audio_mono_16khz, DEST_FOLDER, generate_output_file_name)
    # update the file count
    global files_transformed
    files_transformed += 1
    print(f"Number of files transformed: {files_transformed}", end='\r')


"""
Convert all the audio files in the given folder to mono & 16kHz 
and export the converted files to the destination folder. 
The orginal files will remain unchanged.

    folder: the folder to convert
"""
def convert_all_audio_files_mono_16khz(folder: str) -> None:
    # get all the files in the folder 
    # including within subfolders
    all_files = fh.make_path_list(folder)
    # for each of the files, convert it in place
    for file in all_files:
            convert_audio_file_mono_16khz(file)

"""
generate the output file path for the mono 16kHz file
Format: "{file_name}_mono_16khz.wav"

    file_name: the name of the original file to be converted
"""
def generate_output_file_name(file_name: str) -> None: 
    return f"{file_name}_mono_16khz.wav"




#---------------------------------------#
main()
#---------------------------------------#