import os
import pandas as pd

# Mapping des classes ISIC/HAM10000 → indices
CLASS_NAMES = {
    'nv': 0,    # Naevus mélanocytaire (grain de beauté normal)
    'mel': 1,   # Mélanome
    'bkl': 2,   # Kératose bénigne
    'bcc': 3,   # Carcinome basocellulaire
    'akiec': 4, # Kératose actinique
    'vasc': 5,  # Lésion vasculaire
    'df': 6     # Dermatofibrome
}

def prepare_dataframe(metadata_path: str, images_dir: str) -> pd.DataFrame:
    """
    Charge un CSV de métadonnées et produit un DataFrame prêt à l'emploi
    avec colonnes `filepath` et `label`.
    ``metadata_path`` : chemin vers le fichier CSV (HAM10000, ISIC,...)
    ``images_dir`` : dossier contenant les images JPG.
    """
    df = pd.read_csv(metadata_path)
    if 'dx' not in df.columns or 'image_id' not in df.columns:
        raise ValueError("Le CSV ne contient pas les colonnes attendues `dx` et `image_id`.")

    # convertir les libellés en indices
    df['label'] = df['dx'].map(CLASS_NAMES)
    df['filepath'] = df['image_id'].apply(lambda x: os.path.join(images_dir, f"{x}.jpg"))

    # ne garder que les fichiers qui existent physiquement
    df = df[df['filepath'].apply(os.path.exists)].reset_index(drop=True)
    print(f"Total images disponibles : {len(df)}")
    print(df['dx'].value_counts())
    return df


def split_data(df: pd.DataFrame, seed: int = 42):
    """
    Découpe en train/validation/test (70/15/15) de manière stratifiée.
    Renvoie (train_df, val_df, test_df).
    """
    from sklearn.model_selection import train_test_split

    train_df, temp_df = train_test_split(df, test_size=0.3,
                                          stratify=df['label'], random_state=seed)
    val_df, test_df = train_test_split(temp_df, test_size=0.5,
                                       stratify=temp_df['label'], random_state=seed)
    print(f"Train : {len(train_df)} | Val : {len(val_df)} | Test : {len(test_df)}")
    return train_df, val_df, test_df


def create_generators(train_df, val_df, test_df,
                      img_size=(224, 224), batch_size=32):
    """
    Crée des générateurs Keras avec augmentation pour l'entraînement.
    Les labels sont castés en chaîne car flow_from_dataframe attend des strings.
    """
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    # augmentation léger pour le train
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        vertical_flip=True,
        zoom_range=0.1
    )

    val_datagen = ImageDataGenerator(rescale=1./255)

    # transformer les labels en strings pour éviter l'erreur de Keras
    for df in (train_df, val_df, test_df):
        df['label'] = df['label'].astype(str)

    train_gen = train_datagen.flow_from_dataframe(
        train_df, x_col='filepath', y_col='label',
        target_size=img_size, batch_size=batch_size,
        class_mode='sparse', shuffle=True
    )
    val_gen = val_datagen.flow_from_dataframe(
        val_df, x_col='filepath', y_col='label',
        target_size=img_size, batch_size=batch_size,
        class_mode='sparse', shuffle=False
    )
    test_gen = val_datagen.flow_from_dataframe(
        test_df, x_col='filepath', y_col='label',
        target_size=img_size, batch_size=batch_size,
        class_mode='sparse', shuffle=False
    )
    return train_gen, val_gen, test_gen
