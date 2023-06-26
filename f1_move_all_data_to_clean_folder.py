# Internal helpers and definitions
import h_folder_nav_helpers as fh
import h_FOLDER_DEFINITIONS as fdef
# folder navigation modules
import shutil
import os



#---------------------------------------#
# CONSTANT DEFINITIONS
#---------------------------------------#
# Path to the raw data
SOURCE_FOLDER = fdef.RAW_DATA_FOLDER
# Path to the final data
DEST_FOLDER = fdef.FINAL_DATA_FOLDER
# Location of the clean data folder
CLEAN_DATA_LOCATION = fdef.CLEAN_DATA_LOCATION
#---------------------------------------#

#---------------------------------------#
# GOBAL VARIABLE TRACKERS
#---------------------------------------#
# keep track of the number of files transfered
pos_file_num = 1 # for positive files
neg_file_num = 1 # for negative files
file_num_counts = {} # fo the number of files in each category
#---------------------------------------#



# main function
def main():
    fh.clean_folder(DEST_FOLDER)
    move_files_from_all_sources(SOURCE_FOLDER)



"""
Move files from the given folder to the final data folder.
This function assumes that the files are in the correct format and have been cleaned. 

    souce_folder: the data source we are looking at  e.g. "1_Kaggle"
"""
def move_files_from_folder(source_folder: str) -> None:
    # go into the clean data folder
    data_folder = os.path.join(SOURCE_FOLDER, source_folder)
    clean_folder = os.path.join(data_folder, CLEAN_DATA_LOCATION)
    try:
        # for each catgory # i.e. postive or negative
        for category in sorted(os.listdir(clean_folder)):
            category_folder = os.path.join(clean_folder, category)
            if not os.listdir(category_folder): 
                continue

            if category == "Positive":
                # for each sub catagory, e.g. Meow Scratch
                for sub_category in os.listdir(category_folder):
                    sub_category_folder = os.path.join(category_folder, sub_category)

                    # for each file
                    for file in sorted(os.listdir(sub_category_folder)):
                        file_path = os.path.join(sub_category_folder, file)
                        # generate file name
                        new_file_name = generate_audio_file_name(source_folder, sub_category)
                        
                        # find the final location
                        final_location = os.path.join(DEST_FOLDER, f"{category}/{sub_category}/{new_file_name}")
                        move_file_and_rename(file_path, final_location)

            elif category == "Negative":
                files = sorted(fh.make_path_list(category_folder))
                # for every wav file in file tree of category_folder
                for file_path in files:
                    # if the file is not a wav, or is a 48kHz sample, skip it
                    if not file_path.endswith('.wav') or is_48khz(file_path):
                        continue
                        
                    # generate file name
                    new_file_name = generate_audio_file_name(source_folder, category)

                    # find the final location
                    final_location = os.path.join(DEST_FOLDER, f"{category}/{category}/{new_file_name}")
                    move_file_and_rename(file_path, final_location) # copy the file to the new location

            else:
                print(f"Category not found, skipping! Expected value in [\"Positive\", \"Negative\"], got {category}")

    except Exception as e:
        print(f'Folder cannot be scraped {clean_folder}: {e}')

"""
Generate a name for the current audio file.
Format: "{num}.wav"

Where num is equal to the number file in the given category
i.e Audio file "7.wav" would be the 7th audio chunk collected form 
the source in that specific subcategory.

    source_folder: the data source we are looking at  e.g. "1_Kaggle"
    category: the category of the file, e.g. "Annoyance_Meow"

    returns: the new file name
"""
def generate_audio_file_name(source_folder: str, category: str) -> str:
    # retrive the current running total of files processed
    global pos_file_num
    global neg_file_num
    global file_num_counts

    # convert to the standard format
    category = category.lower().replace("_", "-")
    # increment the respective count
    if category == "negative":
        neg_file_num += 1
    else:
        pos_file_num += 1
    # grab the count for the current category
    curr_file_num = file_num_counts.get(category, 1)

    # = catagory_filenum_iteration__source
    new_file_name = f"{category}_{curr_file_num:06}_{int((source_folder.split('_')[0])):03}.wav"
    # increment the respective count
    file_num_counts[category] = curr_file_num + 1
    return new_file_name


"""
Filters for the 48kHz samples in the negative CHiME dataset (key num 3).
It will return true if the file is a 48kHz sample (as defined by the 
CHiME dataset documentation), false otherwise.

    filepath: the path to the file we are checking

    retuns: true if the file is a 48kHz sample, false otherwise
"""
def is_48khz(filepath: str) -> bool:
    filename = os.path.basename(filepath)
    name_without_extension = os.path.splitext(filename)[0]
    return name_without_extension.split('.')[-1] == "48kHz"

"""
Move the file to the given location and inform the user of the move

    source: the path to the file we are moving
    destination: the path to the new location of the file
"""
def move_file_and_rename(source, destination) -> None:
    global pos_file_num
    global neg_file_num

    # If the location doesnt exist, create it
    dest_folder = os.path.dirname(destination)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        print(f"Directory '{dest_folder}' created.")
    # Copy the file
    shutil.copy(source, destination)
    # inform the user of the new file
    print(f'Number of files tranfered: Positive: {pos_file_num}, Negative: {neg_file_num}', end='\r')

"""
Move files from all the sources in the given parent folder

    source_containing_folder: the folder containing all the sources
"""
def move_files_from_all_sources(source_containing_folder) -> None:
    print(f"Transfering...")
    # for each source folder:
    for source in sorted(os.listdir(source_containing_folder)):
        move_files_from_folder(source)
    print(f"Transfering finished")




#---------------------------------------#
main()
#---------------------------------------#

