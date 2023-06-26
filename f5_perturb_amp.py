# Internal helpers and definitions
import h_folder_nav_helpers as fh
import h_FOLDER_DEFINITIONS as fdef
# folder navigation modules
import os
# audio processing modules
from pydub import AudioSegment
# display the wav files amp
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.io import wavfile



#---------------------------------------#
# AMPLLITUDE MODULATION OPTIONS         #
#---------------------------------------#
# the amps which we wish to perturb the audio files by
# largest to smallest
AMPS_TO_PERTURB_DB = [15, 5, 0, -5, -15]
#---------------------------------------#

#---------------------------------------#
# CONSTANT DEFINITIONS                  #
#---------------------------------------#
# path to the targeted and trimed data folder 
SOURCE_FOLDER = fdef.TARGETED_1_2S_DATA_FOLDER
# path to the perturbed amps data folder 
DEST_FOLDER = fdef.PERTURBED_AMP_DATA_FOLDER
# the categories that we want to process
# if none, then all categories will be processed
CATEGORIES_TO_PROCESS = None
# if we wish to first clean out the destionation folder
CLEAN_DEST = False
#---------------------------------------#

#---------------------------------------#
# GRAPH DISPLAY OPTIONS                 #
#---------------------------------------#
# the files that are to be graphed
WAVS_TO_SHOW = [1, 2, 3, 4, 5]
# whether to show the graphs of the audio files being normaised
SHOW_DIFF_AMP_GRAPHS = True
# the colours for the diff amp graphs
DIFF_AMP_COLOURS = ['lightcoral', 'orange', 'darkseagreen', 
                    'lightskyblue', 'plum']
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
    if CLEAN_DEST: 
        fh.clean_folder(DEST_FOLDER)
    perturb_amp_of_all_files(SOURCE_FOLDER)



"""
generate 5 new wav files at differnt amplitudes
"""
def perturb_amp_of_file(file): 
    new_files = []
    # create the 5 new audio files
    for amp in AMPS_TO_PERTURB_DB:
        # perturb the amplitude of the audio file
        audio = AudioSegment.from_file(file)

        # apply db change to the audio file
        perturbed_audio = audio.apply_gain(amp)  
        # generate a tag for that amp perturbation
        amp_pert_tag = generate_amp_pert_tag(amp)

        # save the new audio file
        output_path = fh.save_new_wav(file, perturbed_audio, DEST_FOLDER, 
                                      generate_output_file_name, amp_pert_tag) 
        # add the new file to the list of files generated from that snippit
        new_files.append(output_path) 

    # update the file count
    global files_transformed
    files_transformed += 1
    print(f"Number of files transformed: {files_transformed}", end='\r')

    # we will display a subset of the converted wav files
    if SHOW_DIFF_AMP_GRAPHS and files_transformed in WAVS_TO_SHOW:
        display_diff_amps_graph(new_files)
        

"""
generate the amp perturbation tag
that will go onto the file name
"""
def generate_amp_pert_tag(amp):
    if amp < 0: # if the amp is a decrease
        tag = f"-{abs(amp):02}dB"
    else: # if the amp is a increase
        tag = f"+{abs(amp):02}dB"
    return tag


"""
generate the output file path
"""
def generate_output_file_name(file_name, end_tag=""): 
    name_sections = file_name.split("_")
    source_info = "_".join(name_sections[:3])
    property_info = "_".join(name_sections[3:])
    return f"{source_info}_{end_tag}_{property_info}.wav"



"""
convert all the audio files in the folder to have normalised amplitude
"""
def perturb_amp_of_all_files(folder):
    # get all the files in the folder 
    # including within subfolders
    all_files = fh.make_path_list(folder)
    
    # for each of the files, convert it in place
    for file in all_files:
        if not CATEGORIES_TO_PROCESS or fh.get_category(file) in CATEGORIES_TO_PROCESS:
            perturb_amp_of_file(file)

"""
display the amp graphs of the given files
all the perturbations (files in list) will be overlayed on top of eachother
"""
def display_diff_amps_graph(files):
    # for each of the generated audio files
    for i, file in enumerate(files):
        # Load the audio file
        sample_rate, audio_data = wavfile.read(file)
        # Extract the amplitude values
        amplitude = audio_data / fdef.MAX_16BIT_AMP
        # Create the time axis
        time = np.arange(0, len(amplitude)) / sample_rate

        # we want to overlay the amps on top of eachother
        # the label will be the associated amp perterbation
        plt.plot(time, amplitude, color=DIFF_AMP_COLOURS[i], 
                 label=f"{AMPS_TO_PERTURB_DB[i]}dB")

    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid(True)

    # Display the legend
    plt.legend(loc='upper right', title='Legend', fontsize='medium')
    # put the title as the file source part of the file name
    file_name = "_".join(os.path.basename(files[0]).split("_")[:3])
    plt.suptitle(file_name)
    # Adjust the spacing between subplots
    plt.tight_layout()

    # Display the plot
    plt.show()



#---------------------------------------#
main()
#---------------------------------------#