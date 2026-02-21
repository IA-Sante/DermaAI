"""
data_loader.py – Chargement des données HAM10000 (train / val / test).

Utilise les CSV générés par preprocess.py et retourne des
tf.data.Dataset prêts à l'emploi.
"""

import os
from typing import Tuple

import pandas as pd
import tensorflow as tf

# Classes du dataset HAM10000 (ordre alphabétique → index 0-6)
CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}

IMG_SIZE = (224, 224)
AUTOTUNE = tf.data.AUTOTUNE


# ---------------------------------------------------------------------------
# Helpers bas niveau
# ---------------------------------------------------------------------------

def _decode_img(path: str) -> tf.Tensor:
    """Lit une image JPEG/PNG et la normalise entre 0 et 1."""
    raw = tf.io.read_file(path)
    img = tf.image.decode_jpeg(raw, channels=3)
    img = tf.image.resize(img, IMG_SIZE)
    img = tf.cast(img, tf.float32) / 255.0
    return img


def _augment(img: tf.Tensor) -> tf.Tensor:
    """Augmentation légère pour l'entraînement."""
    img = tf.image.random_flip_left_right(img)
    img = tf.image.random_flip_up_down(img)
    img = tf.image.random_brightness(img, max_delta=0.1)
    img = tf.image.random_contrast(img, lower=0.9, upper=1.1)
    return img


# ---------------------------------------------------------------------------
# API publique
# ---------------------------------------------------------------------------

def load_split(csv_path: str, batch_size: int = 32,
               augment: bool = False,
               shuffle: bool = False) -> tf.data.Dataset:
    """
    Crée un tf.data.Dataset à partir d'un fichier CSV de split.

    Le CSV doit contenir les colonnes ``path`` et ``label``.

    Args:
        csv_path:   Chemin vers le fichier CSV
                    (train.csv / val.csv / test.csv).
        batch_size: Taille des batches.
        augment:    Applique l'augmentation si ``True`` (train seulement).
        shuffle:    Mélange les données si ``True`` (train seulement).

    Returns:
        tf.data.Dataset de tuples (image_tensor, label_index).
    """
    df = pd.read_csv(csv_path)
    paths = df["path"].tolist()
    labels = [CLASS_TO_IDX[lbl] for lbl in df["label"].tolist()]

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))

    if shuffle:
        ds = ds.shuffle(buffer_size=len(paths), reshuffle_each_iteration=True)

    def process(path, label):
        img = _decode_img(path)
        if augment:
            img = _augment(img)
        return img, label

    ds = ds.map(process, num_parallel_calls=AUTOTUNE)
    ds = ds.batch(batch_size)
    ds = ds.prefetch(AUTOTUNE)
    return ds


DatasetTuple = Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]


def get_datasets(splits_dir: str = "data/splits",
                 batch_size: int = 32) -> DatasetTuple:
    """
    Retourne les trois datasets (train, val, test).

    Args:
        splits_dir: Dossier contenant train.csv, val.csv et test.csv.
        batch_size: Taille des batches.

    Returns:
        Tuple (train_ds, val_ds, test_ds).
    """
    train_ds = load_split(
        os.path.join(splits_dir, "train.csv"),
        batch_size=batch_size,
        augment=True,
        shuffle=True,
    )
    val_ds = load_split(
        os.path.join(splits_dir, "val.csv"),
        batch_size=batch_size,
    )
    test_ds = load_split(
        os.path.join(splits_dir, "test.csv"),
        batch_size=batch_size,
    )
    return train_ds, val_ds, test_ds


if __name__ == "__main__":
    _train_ds, _val_ds, _test_ds = get_datasets()
    print("Train batches :", len(_train_ds))
    print("Val   batches :", len(_val_ds))
    print("Test  batches :", len(_test_ds))
