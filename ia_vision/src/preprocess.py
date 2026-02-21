"""
preprocess.py – Prétraitement du dataset HAM10000.

Usage:
    python preprocess.py --raw_dir data/raw --out_dir data/processed \
                         --metadata data/raw/HAM10000_metadata.csv
"""

import argparse
import os
import shutil

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

# Classes du dataset HAM10000
CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
IMG_SIZE = (224, 224)


def resize_and_save(src_path: str, dst_path: str, size: tuple = IMG_SIZE) -> None:
    """Redimensionne une image et la sauvegarde."""
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    img = Image.open(src_path).convert("RGB")
    img = img.resize(size, Image.LANCZOS)
    img.save(dst_path)


def preprocess_dataset(raw_dir: str, out_dir: str, metadata_csv: str) -> pd.DataFrame:
    """
    Lit le fichier metadata, redimensionne chaque image et
    l'enregistre dans out_dir/<label>/.

    Returns:
        DataFrame avec colonnes ['image_id', 'label', 'path'].
    """
    df = pd.read_csv(metadata_csv)
    records = []

    for _, row in df.iterrows():
        image_id = row["image_id"]
        label = row["dx"]

        # Cherche l'image dans raw_dir (peut être réparti sur plusieurs sous-dossiers)
        src = None
        for root, _, files in os.walk(raw_dir):
            for fname in files:
                if fname.startswith(image_id) and fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    src = os.path.join(root, fname)
                    break
            if src:
                break

        if src is None:
            continue

        ext = os.path.splitext(src)[1]
        dst = os.path.join(out_dir, label, image_id + ext)
        resize_and_save(src, dst)
        records.append({"image_id": image_id, "label": label, "path": dst})

    return pd.DataFrame(records)


def create_splits(df: pd.DataFrame, splits_dir: str,
                  val_size: float = 0.15, test_size: float = 0.15,
                  random_state: int = 42) -> None:
    """Crée et sauvegarde les fichiers CSV train/val/test."""
    os.makedirs(splits_dir, exist_ok=True)

    train_df, tmp_df = train_test_split(
        df, test_size=val_size + test_size,
        stratify=df["label"], random_state=random_state
    )
    rel_test = test_size / (val_size + test_size)
    val_df, test_df = train_test_split(
        tmp_df, test_size=rel_test,
        stratify=tmp_df["label"], random_state=random_state
    )

    train_df.to_csv(os.path.join(splits_dir, "train.csv"), index=False)
    val_df.to_csv(os.path.join(splits_dir, "val.csv"), index=False)
    test_df.to_csv(os.path.join(splits_dir, "test.csv"), index=False)

    print(f"Train : {len(train_df)} | Val : {len(val_df)} | Test : {len(test_df)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prétraitement HAM10000")
    parser.add_argument("--raw_dir", default="data/raw")
    parser.add_argument("--out_dir", default="data/processed")
    parser.add_argument("--splits_dir", default="data/splits")
    parser.add_argument("--metadata", default="data/raw/HAM10000_metadata.csv")
    args = parser.parse_args()

    print("Prétraitement en cours…")
    df = preprocess_dataset(args.raw_dir, args.out_dir, args.metadata)
    print(f"{len(df)} images traitées.")

    create_splits(df, args.splits_dir)
    print("Splits sauvegardés dans", args.splits_dir)


if __name__ == "__main__":
    main()
