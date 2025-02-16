import glob
import os
import sys
import argparse
import numpy as np
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from utils import audio
import utils.utils as utils
from tqdm import tqdm
import pyworld as pw
from random import shuffle

import warnings
warnings.filterwarnings("ignore")

def extract_mel(wav, hparams):
    mel_spectrogram = audio.melspectrogram(wav, hparams).astype(np.float32)
    return mel_spectrogram.T, wav

def extract_pitch(wav, hps):
    # rapt may be better
    f0, _ = pw.harvest(wav.astype(np.float64),
                   hps.sample_rate,
                   frame_period=hps.hop_size / hps.sample_rate * 1000)
    return f0

def process_utterance(hps, data_root, item):
    out_dir = data_root

    wav_path = os.path.join(data_root, "wavs",
                            "{}.wav".format(item))
    wav = audio.load_wav(wav_path,
                         raw_sr=hps.data.sample_rate,
                         target_sr=hps.data.sample_rate,
                         win_size=hps.data.win_size,
                         hop_size=hps.data.hop_size)

    mel, _ = extract_mel(wav, hps.data)
    out_mel_dir = os.path.join(out_dir, "mels")
    os.makedirs(out_mel_dir, exist_ok=True)
    mel_path = os.path.join(out_mel_dir, item)
    np.save(mel_path, mel)

    pitch = extract_pitch(wav, hps.data)
    out_pitch_dir = os.path.join(out_dir, "pitch")
    os.makedirs(out_pitch_dir, exist_ok=True)
    pitch_path = os.path.join(out_pitch_dir, item)
    np.save(pitch_path, pitch)


def process(args, hps, data_dir):
    print(os.path.join(data_dir, "wavs"))
    if(not os.path.exists(os.path.join(data_dir, "file.list"))):
        with open(os.path.join(data_dir, "file.list") , "w") as out_file:
            files = os.listdir(os.path.join(data_dir, "wavs"))
            files = [i for i in files if i.endswith(".wav")]
            for f in files:
                out_file.write(f.strip().split(".")[0] + '\n')
    metadata = [
        item.strip() for item in open(
            os.path.join(data_dir, "file.list")).readlines()
    ]
    executor = ProcessPoolExecutor(max_workers=args.num_workers)
    results = []
    for item in metadata:
        results.append(executor.submit(partial(process_utterance, hps, data_dir, item)))
    return [result.result() for result in tqdm(results)]

def split_dataset(data_dir):
    metadata = [
        item.strip() for item in open(
            os.path.join(data_dir, "file.list")).readlines()
    ]
    shuffle(metadata)
    train_set = metadata[:-2]
    test_set =  metadata[-2:]
    with open(os.path.join(data_dir, "train.list"), "w") as ts:
        for item in train_set:
            ts.write(item+"\n")
    with open(os.path.join(data_dir, "test.list"), "w") as ts:
        for item in test_set:
            ts.write(item+"\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',
                        default='egs/visinger2/config.json',
                        help='json files for configurations.')
    parser.add_argument('--num_workers', type=int, default=int(cpu_count()) // 2)

    args = parser.parse_args()
    hps = utils.get_hparams_from_file(args.config)
    spklist = [spk for spk in os.listdir("data") if os.path.isdir(f"data/{spk}") and not os.path.exists(f"data/{spk}/test.list")]
    for spk in tqdm(spklist):
        print(f"preprocessing {spk}")
        data_dir = f"data/{spk}"
        process(args, hps, data_dir)
        split_dataset(data_dir)

if __name__ == "__main__":
    main()
