from mido import MidiFile
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

from music21 import converter, instrument, note, chord, stream
import pypianoroll


class LakhDatasetHandler:

    def __init__(self, root_dir) -> None:
        self.root_dir = root_dir
        self.data_dir = "f{root_dir}/Lakh Piano Dataset/lpd_5/lpd_5_cleansed"
        self.results_path = os.path.join(root_dir, 'Lakh Piano Dataset', 'Metadata')

        cleansed_ids = pd.read_csv(os.path.join(root_dir, 'Lakh Piano Dataset', 'cleansed_ids.txt'), delimiter = '    ', header = None)
        self.lpd_to_msd_ids = {a:b for a, b in zip(cleansed_ids[0], cleansed_ids[1])}
        self.msd_to_lpd_ids = {a:b for a, b in zip(cleansed_ids[1], cleansed_ids[0])}
        self.midi_dir = f'{root_dir}/Lakh Piano Dataset/lpd_5_midi'


    # Utility functions for retrieving paths
    def msd_id_to_dirs(self, msd_id):
        """Given an MSD ID, generate the path prefix.
        E.g. TRABCD12345678 -> A/B/C/TRABCD12345678"""
        return os.path.join(msd_id[2], msd_id[3], msd_id[4], msd_id)


    def msd_id_to_h5(self, msd_id):
        """Given an MSD ID, return the path to the corresponding h5"""
        return os.path.join(self.results_path, 'lmd_matched_h5',
                            self.msd_id_to_dirs(msd_id) + '.h5')

    # Load the midi npz file from the LMD cleansed folder
    def get_midi_npz_path(self, msd_id, midi_md5):
        return os.path.join(self.data_dir,
                            self.msd_id_to_dirs(msd_id), midi_md5 + '.npz')
    

    def parse_to_midi(self):
        for msd_file_name in list(self.lpd_to_msd_ids.values())[:100]:
            lpd_file_name = self.msd_to_lpd_ids[msd_file_name]

            npz_path = self.get_midi_npz_path(msd_file_name, lpd_file_name)
            pianoroll = pypianoroll.load(npz_path)

            pypianoroll.write(f"{self.midi_dir}/{lpd_file_name}.mid", pianoroll)
