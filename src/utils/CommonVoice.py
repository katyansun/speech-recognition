import torch
import os
import pandas as pd
import numpy as np

import torchaudio

from torch.utils.data import Dataset

from typing import Union, Dict, Optional

from .preprocess import Preprocessing

class CommonVoice(Dataset):
    
    """
    Utility Class for loading the Common Voice Dataset.
    """
    
    def __init__(self, dataset_dir: str,  subset_name: str = None, subset_path: Optional[str] = None, out_channels: int = 2, out_sampling_rate: int = 16000, tokenizer = None):
        
 
        """
        Iterate over a subset CommonVoice dataset.
        
        Args:
        ----------
        dataset_dir: str
            The path where train.tsv, test.tsv and dev.tsv are located.
        
        subset_path: str
            Filename of the dataset tsv. Must contain columns path and sentence. Cannot be used with subset_name. 
        
        subset_name: str [train, test, dev]
            Loads one of train.tsv, test.tsv or dev.tsv from the dataset_dir. Cannot be used with subset_path.
        
        out_channels: int 
            Number of output channels for audio. 
            Mono = 1, Stereo = 2.
        
        out_sampling_rate: int
            sampling_rate used for standardizing.
        
        tokenizer: transformers.PreTrainedTokenizerFast
            tokenizer: tokenizer from huggingface used for tokenizing.
        
        Returns:
        ----------
        CommonVoice Dataset object.
        
        """
        
        super(CommonVoice).__init__()
                
        self.split_type = subset_name
        self.dataset_path = dataset_dir
        
        ##Check that out_sampling_rate is an integer. Will probably need to specify how to convert Khz to Hz.
        assert isinstance(out_sampling_rate, int)
        self.out_sampling_rate = out_sampling_rate
        
        ##Check how many output channels are needed.
        if out_channels in [1, 2]:
            self.out_channels = out_channels
        else:
            raise ValueError("Only Mono (out_channels = 1) and Stereo (out_channels = 2) Supported.")
        
        ##Check that dataset exists in the path specified and add clips path.
        if os.path.exists(dataset_dir):
            self.clips_path = os.path.join(dataset_dir, 'clips')
        else:
            raise ValueError(f"{dataset_dir} doesn't exist, please provide a valid path to the dataset.")
        
        ##Check that split_type is one of train, test, dev.
        if subset_path == None and subset_name != None:

            if subset_name in ['train', 'test' , 'dev']:
                fullpath = os.path.join(dataset_dir, subset_name + '.tsv')
            else:
                raise ValueError("split_type must be one of train, test or dev")

        elif subset_path != None and subset_name != None:
            raise ValueError("Please only use one of [split_type] or [data_file_path].")

        elif subset_path == None and subset_name == None:
            raise ValueError("Please pass value for either data_file_path or split_type.")

        else:
            fullpath = subset_path
            
        ## Load the dataframe
        self.dataframe = pd.read_csv(fullpath, sep = '\t')
        
        ## Check if tokenizer is passed
        
        if tokenizer == None:
            raise ValueError("tokenizer cannot be None.")
        else:
            self.tokenizer = tokenizer
            
        ## Initialize Preprocessing
        
        self.preprocessing = Preprocessing(out_channels= self.out_channels, out_sampling_rate = self.out_sampling_rate, tokenizer = self.tokenizer)
        
        
    def __len__(self) -> int:
        return len(self.dataframe)
        
    
    def __getitem__(self, idx: Union[int, torch.Tensor, np.ndarray]) -> Dict[str, torch.Tensor]:
        
        if isinstance(idx, torch.Tensor):
            idx = list(idx)
            
        item = self.dataframe.iloc[idx]
        
        sentence = item['sentence']
        
        ## Don't need it right now, enable if needed later
        
        # age = item['age']
        # gender = item['gender']
        # accent = item['accents']
        
        audio_file_path = os.path.join(self.clips_path, item['path'])
        
        waveform, source_sampling_rate = torchaudio.load(audio_file_path)
        waveform, out_sampling_rate = self.preprocessing.preprocess_waveform(waveform, source_sampling_rate)
        
        melspec = self.preprocessing.extract_features(waveform)
        
        # item = {'waveform': waveform, 'sentence': sentence, 'age': age, 'gender' : gender, 'accent': accent}
        
        item = {'waveform': waveform, 'sentence': sentence, 'melspec': melspec}
        
        return item
    
    
    def __repr__(self):
        return \
    f"""
    CommonVoice Dataset
    -------------------
    
    Loading {self.split_type}.tsv from {os.path.abspath(self.dataset_path)} directory.
        
    Number of Examples: {self.__len__()}
    
    Args:
        Sampling Rate: {self.out_sampling_rate}
        Output Channels: {self.out_channels}
    """
    