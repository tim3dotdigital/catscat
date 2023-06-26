# Internal helpers and definitions
import h_FOLDER_DEFINITIONS as fdef
# modules used for folder naviation
import os
# modules used for audio processing
from pydub import AudioSegment
import librosa
import wave
# used for graphing the audio files
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.io import wavfile




#---------------------------------------#
# FOLDER HELPERS
#---------------------------------------#

# find a list of all the paths in the given direcotry
def make_path_list(directory):
    path_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            path_list.append(file_path)
    return path_list

# get the category of the file
def get_category(file):
    return os.path.basename(file).split("_")[0]

# clean all files from the given directory
def clean_folder(directory):
    print(f"Cleaning...")
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
    print(f"Cleaning finished")




#---------------------------------------#
# AUDIO FILE MODIFCATION HELPERS
#---------------------------------------#

"""
save the new wav file to the relevant folder
    file_path: is the path to the original file
"""
def save_new_wav(file_path, new_audio, dest_partent_folder, generate_output_file_name, end_tag=None):
    # find the path the relevant subfolder within the data folder
    # e.g. we want /Positive/Annoyance_Meow/
    # Extract the last two subfolders
    subfolders = os.path.dirname(file_path).split(os.path.sep)[-2:]
    # Join the subfolders back into a path
    subfolder_path = os.path.sep.join(subfolders)

    # define the new data location folder
    new_file_location = os.path.join(dest_partent_folder, subfolder_path)
    # make the the needed direcotries if not present
    os.makedirs(new_file_location, exist_ok=True)

    # define the output filename
    # Extract the old file name without the extension
    old_file_name = os.path.splitext(os.path.basename(file_path))[0]
    # design the new file name
    if end_tag: # if we have a special end tag
        new_file_name = generate_output_file_name(old_file_name, end_tag)
    else:
        new_file_name = generate_output_file_name(old_file_name)

    # Export the mono audio to the specified folder
    output_path = os.path.join(new_file_location, new_file_name)
    new_audio.export(output_path, format='wav')

    return output_path



#---------------------------------------#
# AUDIO FILE GRAPHING HELPERS
#---------------------------------------#

"""
display the properties of the audio file
"""
def display_wav_data(file):
    # Open the WAV file
    with wave.open(file, 'rb') as wav_file:
        # Get the number of channels
        num_channels = wav_file.getnchannels()
        print("Number of Channels:", num_channels)

        # Get the sampling frequency
        sample_rate = wav_file.getframerate()
        print("Sampling Frequency:", sample_rate)

"""
compare the two given audio files highlighing the section in the first audio file
that exceeds the amplitude threshold and was thus extracted to make the second audio file
    old_file: the original audio file
    new_file: the extracted audio file
    first_exceeding_time: the time in seconds at which the audio first exceeds the amplitude threshold
    last_exceeding_time: the time in seconds at which the audio last exceeds the amplitude threshold
"""
def compare_extracted_target_graph(old_file, new_file, first_exceeding_time, last_exceeding_time):
    # Load the first WAV file using PyDub
    audio_file_old = AudioSegment.from_wav(old_file)
    # Convert the audio into a NumPy array
    audio_array_old = np.array(audio_file_old.get_array_of_samples()) / fdef.MAX_16BIT_AMP
    # Load the second WAV file using PyDub
    audio_file2 = AudioSegment.from_wav(new_file)
    # Convert the audio into a NumPy array
    audio_array2 = np.array(audio_file2.get_array_of_samples()) / fdef.MAX_16BIT_AMP
    # Create the time array for the first waveform
    time1 = np.arange(len(audio_array_old)) / audio_file_old.frame_rate
    # Create the time array for the second waveform
    time2 = np.arange(len(audio_array2)) / audio_file2.frame_rate

    # Create subplots with shared y-axis
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)

    # plot the org audio file
    time = np.arange(len(audio_array_old)) / audio_file_old.frame_rate
    ax1.plot(time, audio_array_old, color='lightskyblue')

    # Highlight the exceeding section
    # Find the indices within the specified range
    target_indices = np.where((time >= first_exceeding_time) & (time <= last_exceeding_time))[0]
    target_leadin_indices = np.where((time >= first_exceeding_time - LEAD_IN_TIME) 
                                     & (time <= last_exceeding_time + LEAD_IN_TIME))[0]
    # Highlight the lead in time
    ax1.plot(time[target_leadin_indices], audio_array_old[target_leadin_indices], color='pink')
    # Highlight the points within the specified range in red
    ax1.plot(time[target_indices], audio_array_old[target_indices], color='lightcoral')
    # Set labels and title for the graph
    ax1.set(xlabel='Time (seconds)', ylabel='Amplitude', title='Original File')
    ax1.grid(True)

    # Plot trimed target audio file
    ax2.plot(time2, audio_array2, color='lightcoral')
    ax2.set(xlabel='Time (seconds)', ylabel='Amplitude', title='Target File')
    ax2.grid(True)

    file_name = "_".join(os.path.basename(old_file).split("_")[:3])
    fig.suptitle(file_name)
    # Adjust the spacing between subplots
    plt.tight_layout()
    # Show the graph
    plt.show()

"""
display two graphs amplitudes overlayed on top of each other
"""
def display_amp_graph(file_old, file_new):
    # OLD AUDIO FILE
    # Load the audio file
    o_sample_rate, o_audio_data = wavfile.read(file_old)
    # Extract the amplitude values
    o_amplitude = o_audio_data / fdef.MAX_16BIT_AMP
    # Create the time axis
    o_time = np.arange(0, len(o_amplitude)) / o_sample_rate

    # NEW AUDIO FILE
    # Load the audio file
    n_sample_rate, n_audio_data = wavfile.read(file_new)
    # Extract the amplitude values
    n_amplitude = n_audio_data / fdef.MAX_16BIT_AMP
    # Create the time axis
    n_time = np.arange(0, len(n_amplitude)) / n_sample_rate

    # Create the figure and subplots
    # if the old amp is larger i.e. we are decreasing the amp
    if max(o_amplitude) > max(n_amplitude):
        # we want to overlay the new amp on top of the old amp
        plt.plot(o_time, o_amplitude, color='lightskyblue', label="Original Audio")
        plt.plot(n_time, n_amplitude, color='lightcoral', label="Normalised Audio")
    else: # if the new amp is larger i.e. we are increasing the amp
        # we want to overlay the old amp on top of the new amp
        plt.plot(n_time, n_amplitude, color='lightcoral', label="Normalised Audio")
        plt.plot(o_time, o_amplitude, color='lightskyblue', label="Original Audio")

    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    #ax1.set_title('Old Audio')
    plt.grid(True)

    # Display the legend
    plt.legend(loc='upper right', title='Legend', fontsize='medium')

    # put the title as the file source part of the file name
    file_name = "_".join(os.path.basename(file_old).split("_")[:3])
    plt.suptitle(file_name)
    # Adjust the spacing between subplots
    plt.tight_layout()
    # Display the plot
    plt.show()