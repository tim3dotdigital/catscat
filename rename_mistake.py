# Internal helpers and definitions=
import h_folder_nav_helpers as fh
import h_FOLDER_DEFINITIONS as fdef

import os


def rename_files(folder):
    for file in fh.make_path_list(folder):
        if is_second_pass(file):
            new_name = os.path.basename(file).replace("centered_1-2s_centered_1-2s", "centered_1-2s")
            os.rename(file, os.path.join(os.path.dirname(file), new_name))

def is_second_pass(file):
    return "2ndpass" in os.path.basename(file)


rename_files(fdef.PERTURBED_AMP_DATA_FOLDER)