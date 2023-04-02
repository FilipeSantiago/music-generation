import numpy as np
import os
from tqdm import tqdm

from music21 import converter, instrument, note, chord, stream
import pypianoroll


class NoteRepresentation:

    def __init__(self, midi_dir) -> None:        
        self.midi_dir = midi_dir
        self.note_to_int = None
        self.int_to_note = None
    
    def get_data(self, sequence_len=32):
        data, all_used_notes = self.__gather_data()
        network_in, network_out = self.__prepare_data_to_train_network(data, all_used_notes, sequence_len)

        n_patterns = len(network_in)
        network_in = np.reshape(network_in, (n_patterns, sequence_len, 1))
        
        return network_in, network_out
    
    def __gather_data(self):
        data = []
        all_used_notes = set()
        for _, _, files in os.walk(f"{self.midi_dir}"):
            for file in files:
                notes, _all_used_notes = self.__get_music_notes(f"{self.midi_dir}/{file}")
                all_used_notes = all_used_notes.union(_all_used_notes)
                data.append(notes)


        return data, all_used_notes

    def __prepare_data_to_train_network(self, data, all_used_notes, sequence_len=32):
        self.note_to_int = dict((note, idx) for idx, note in enumerate(all_used_notes))
        self.int_to_note = dict((idx, note) for idx, note in enumerate(all_used_notes))

        network_in, network_out = self.__prepare_data_songs(data, self.note_to_int, sequence_len=sequence_len)

        return network_in, network_out
   
    def __get_music_notes(self, midi_path):
        all_used_notes = set()

        midi = converter.parse(midi_path)
        s2 = instrument.partitionByInstrument(midi)
        piano_part = None
        # Filter for  only the piano part
        instr = instrument.Piano
        for part in s2:
            if isinstance(part.getInstrument(), instr):
                piano_part = part

        notes_song = []
        if piano_part: # Some songs somehow have no piano parts
            for element in piano_part:
                if isinstance(element, note.Note):
                    # Return the pitch of the single note
                    notes_song.append(str(element.pitch))
                    all_used_notes.add(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    # Returns the normal order of a Chord represented in a list of integers
                    notes_song.append('.'.join(str(n) for n in element.normalOrder))
                    all_used_notes.add('.'.join(str(n) for n in element.normalOrder))

        return notes_song, all_used_notes
    

    def __prepare_data_songs(self, data=None, note_parser=None, sequence_len=32):
        network_in = []
        network_out = []


        study_songs = []
        for song in list(filter(lambda x: len(x) > 0, data)):
            np_song = []
            for note in song:
                np_song.append(note_parser[note])
            study_songs.append(np_song)

        for song in study_songs:

            i = 0
            while i + sequence_len < len(song):

                sequence_in = song[i:i + sequence_len]
                sequence_out = song[i + sequence_len]

                network_in.append(sequence_in)
                network_out.append(sequence_out)
                i += sequence_len

        network_in = np.array(network_in)
        network_out = np.array(network_out)

        return network_in, network_out
