import os
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator

CLASS_NAMES = {
    "nv": 0,
    "mel": 1,
    "bkl": 2,
    "bcc": 3,
    "akiec": 4,
    "vasc": 5,
    "df": 6,
}


def prepare_dataframe(metadata_path: str, images_dir: str) -> pd.DataFrame:
    df = pd.read_csv(metadata_path)
    df["label"] = df["dx"].map(CLASS_NAMES)
    df = df.dropna(subset=["label"]).copy()
    df["label"] = df["label"].astype(int)

    df["filepath"] = df["image_id"].apply(lambda x: os.path.join(images_dir, f"{x}.jpg"))
    df = df[df["filepath"].apply(os.path.exists)].reset_index(drop=True)

    print(f"Total images disponibles : {len(df)}")
    print(df["dx"].value_counts())
    return df


def split_data(df: pd.DataFrame):
    train_df, temp_df = train_test_split(
        df,
        test_size=0.3,
        stratify=df["label"],
        random_state=42,
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        stratify=temp_df["label"],
        random_state=42,
    )
    print(f"Train : {len(train_df)} | Val : {len(val_df)} | Test : {len(test_df)}")
    return train_df, val_df, test_df


def create_generators(train_df, val_df, test_df, img_size=(224, 224), batch_size=32):
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        vertical_flip=True,
        zoom_range=0.1,
    )

    val_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_df = train_df.copy()
    val_df = val_df.copy()
    test_df = test_df.copy()

    train_df["label"] = train_df["label"].astype(str)
    val_df["label"] = val_df["label"].astype(str)
    test_df["label"] = test_df["label"].astype(str)

    train_gen = train_datagen.flow_from_dataframe(
        train_df,
        x_col="filepath",
        y_col="label",
        target_size=img_size,
        batch_size=batch_size,
        class_mode="sparse",
        shuffle=True,
    )
    val_gen = val_datagen.flow_from_dataframe(
        val_df,
        x_col="filepath",
        y_col="label",
        target_size=img_size,
        batch_size=batch_size,
        class_mode="sparse",
        shuffle=False,
    )
    test_gen = val_datagen.flow_from_dataframe(
        test_df,
        x_col="filepath",
        y_col="label",
        target_size=img_size,
        batch_size=batch_size,
        class_mode="sparse",
        shuffle=False,
    )

    return train_gen, val_gen, test_gen


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    metadata = root / "data" / "raw" / "HAM10000_metadata.csv"
    images = root / "data" / "raw" / "images"

    frame = prepare_dataframe(str(metadata), str(images))
    split_data(frame)
