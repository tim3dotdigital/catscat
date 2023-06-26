"""
NOTE that all paths are relative to the catscat_datacollection folder
found at "DD-Data/non-final-data/catscat_datacollection"
"""




#---------------------------------------#
# CONSTANT DEFINITIONS
#---------------------------------------#
# the max amplitude of a 16 bit wav file
MAX_16BIT_AMP = 32768.0

# the time in seconds to lead in and out of the sound of interest
LEAD_IN_TIME = 0.2
# max length that we want our audio files
MAX_LENGTH_S = 2.0
# min length that we want our audio files
MIN_LENGTH_S = 1.0



#---------------------------------------#
# DATA COLLECTION FOLDER PATHS
#---------------------------------------#
# Path to the raw data
RAW_DATA_FOLDER = "../raw-data"

# Location of the clean data folder within raw data folder structure
CLEAN_DATA_LOCATION = "clean"

# Path to the final data
FINAL_DATA_FOLDER = '../../data'



#---------------------------------------#
# DATA PROCESSING FOLDER PATHS
#---------------------------------------#
# path to the mono, 16kHz transformed data folder
MONO_16KHZ_DATA_FOLDER = '../../transformed-data/mono_16khz'

# path to the normalised amplitude data folder
AMP_NORM_DATA_FOLDER = '../../transformed-data/amp_normalised'

# path to the targeted and trimed data folder
TARGETED_1_2S_DATA_FOLDER = '../../transformed-data/targeted_1-2s'

# path to the perturbed amplitudes data folder
PERTURBED_AMP_DATA_FOLDER = '../../transformed-data/amp_perturbed'



#---------------------------------------#
# TEMPORARY DATA STORAGE FOLDER PATHS        
#---------------------------------------#
# folder to store the temp intermediate files
# these are used to store the leftover audio after the 
# target section has been extracted
TEMP_LEFTOVER_FOLDER = "../temp/temp_leftover"
TEMP_NORMALISED_FOLDER = "../temp/temp_norm"
TEMP_FOLDER = "../temp"
#---------------------------------------#



#---------------------------------------#
# TESTING
#---------------------------------------#
# path to the testing folder with small subset of data
TEST_DATA_FOLDER = '../test-data'
TEST_DEST_FOLDER = '../test-dest'


