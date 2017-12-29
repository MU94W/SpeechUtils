import tensorflow as tf
import os
import argparse
import scipy.io.wavfile as siowav
import numpy as np
import tqdm


def get_arguments():
    parser = argparse.ArgumentParser(description="Extract wav from TFRecords file and save.")
    parser.add_argument("--tfrecord_path", "-s", type=str, default="./wav_mel_stftm.tfrecords", help="")
    parser.add_argument("--wav_root", "-d", type=str, default="./wav_recover_within_sess", help="")
    return parser.parse_args()


def parse_single_example(example_proto):
    features = {"sr": tf.FixedLenFeature([], tf.int64),
                "key": tf.FixedLenFeature([], tf.string),
                "frames": tf.FixedLenFeature([], tf.int64),
                "wav_raw": tf.FixedLenFeature([], tf.string),
                "norm_mel_raw": tf.FixedLenFeature([], tf.string),
                "norm_stftm_raw": tf.FixedLenFeature([], tf.string)}
    parsed = tf.parse_single_example(example_proto, features=features)
    sr = tf.cast(parsed["sr"], tf.int32)
    key = parsed["key"]
    frames = tf.cast(parsed["frames"], tf.int32)
    wav = tf.decode_raw(parsed["wav_raw"], tf.int16)
    norm_mel = tf.reshape(tf.decode_raw(parsed["norm_mel_raw"], tf.float32), (frames, 80))
    norm_stftm = tf.reshape(tf.decode_raw(parsed["norm_stftm_raw"], tf.float32), (frames, 513))
    return {"sr": sr, "key": key, "frames": frames, "wav": wav, "norm_mel": norm_mel, "norm_stftm": norm_stftm}


def get_dataset(tfrecord_path):
    dataset = tf.data.TFRecordDataset(tfrecord_path)
    dataset = dataset.map(parse_single_example)
    dataset = dataset.shuffle(10000)
    dataset = dataset.padded_batch(3, padded_shapes={"sr": (),
                                                     "key": (),
                                                     "frames": (),
                                                     "wav": [None],
                                                     "norm_mel": [None, 80],
                                                     "norm_stftm": [None, 513]})
    return dataset


def main():
    args = get_arguments()
    
    data_set = get_dataset(args.tfrecord_path)
    iterator = data_set.make_one_shot_iterator()
    next_item = iterator.get_next()

    sess = tf.Session()
    while True:
        try:
            print(sess.run(tf.shape(next_item["norm_mel"])))
        except Exception as e:
            print(e)

    print("Congratulations!")


if __name__ == "__main__":
    print(__file__)
    main()
