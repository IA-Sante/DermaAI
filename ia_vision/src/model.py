import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
)
from PIL import Image

NUM_CLASSES = 7
IMG_SIZE = (224, 224, 3)

CLASS_INFO = {
    0: {'name': 'nv',    'label': 'Naevus mélanocytaire', 'risk_weight': 0.1},
    1: {'name': 'mel',   'label': 'Mélanome',              'risk_weight': 0.95},
    2: {'name': 'bkl',   'label': 'Kératose bénigne',      'risk_weight': 0.2},
    3: {'name': 'bcc',   'label': 'Carcinome basocellulaire','risk_weight': 0.75},
    4: {'n\u0061me': 'akiec', 'label': 'Kératose actinique',    'risk_weight': 0.6},
    5: {'name': 'vasc',  'label': 'Lésion vasculaire',     'risk_weight': 0.3},
    6: {'name': 'df',    'label': 'Dermatofibrome',        'risk_weight': 0.15},
}


def build_model(num_classes: int = NUM_CLASSES, learning_rate: float = 1e-4):
    """
    Construit un modèle MobileNetV2 pour classification à partir de zéro
    en utilisant transfer learning.
    Renvoie (model, base_model) pour pouvoir dégeler plus tard.
    """
    base_model = MobileNetV2(
        input_shape=IMG_SIZE,
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=IMG_SIZE)
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = models.Model(inputs, outputs)
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model, base_model


def unfreeze_model(model, base_model, fine_tune_at: int = 100):
    """
    Active le fine‑tuning en rendant la base entraînable à partir de
    la couche indiquée.
    """
    base_model.trainable = True
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-5),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    print(f"Fine-tuning activé à partir de la couche {fine_tune_at}")
    return model


def predict_image(image_path: str, model_path: str = None) -> dict:
    """Retourne la prédiction, confiance et score_image du modèle."""
    if model_path is None:
        raise ValueError("Chemin du modèle requis pour la prédiction")
    model = tf.keras.models.load_model(model_path)
    img = Image.open(image_path).convert('RGB').resize(IMG_SIZE[:2])
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    predictions = model.predict(img_array)[0]
    predicted_class = int(np.argmax(predictions))
    confidence = float(predictions[predicted_class])
    score_image = float(np.sum([predictions[i] * CLASS_INFO[i]['risk_weight']
                                for i in range(len(predictions))]))
    return {
        'predicted_class': CLASS_INFO[predicted_class]['label'],
        'confidence': round(confidence, 4),
        'score_image': round(score_image, 4),
        'all_probabilities': {CLASS_INFO[i]['label']: round(float(predictions[i]), 4)
                              for i in range(len(predictions))}
    }

# code utilitaire d'entraînement si exécuté directement
if __name__ == '__main__':
    from preprocess import prepare_dataframe, split_data, create_generators
    # configuration par défaut
    METADATA_PATH = '../data/raw/HAM10000_metadata.csv'
    IMAGES_DIR    = '../data/raw/images/'
    MODEL_SAVE    = '../models/dermai_cnn.h5'
    BATCH_SIZE    = 32
    EPOCHS_PHASE1 = 15
    EPOCHS_PHASE2 = 10

    df = prepare_dataframe(METADATA_PATH, IMAGES_DIR)
    train_df, val_df, test_df = split_data(df)
    train_gen, val_gen, test_gen = create_generators(train_df, val_df, test_df,
                                                      batch_size=BATCH_SIZE)

    callbacks = [
        ModelCheckpoint(MODEL_SAVE, monitor='val_accuracy', save_best_only=True, verbose=1),
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-7, verbose=1)
    ]

    print("\n=== PHASE 1 : Entraînement de la tête ===")
    model, base_model = build_model()
    history1 = model.fit(
        train_gen, validation_data=val_gen,
        epochs=EPOCHS_PHASE1, callbacks=callbacks, verbose=1
    )

    print("\n=== PHASE 2 : Fine-tuning ===")
    model = unfreeze_model(model, base_model, fine_tune_at=100)
    history2 = model.fit(
        train_gen, validation_data=val_gen,
        epochs=EPOCHS_PHASE2, callbacks=callbacks, verbose=1
    )

    print("\n=== ÉVALUATION SUR LE TEST SET ===")
    test_loss, test_acc = model.evaluate(test_gen)
    print(f"Test Accuracy : {test_acc:.4f}")
    print(f"Test Loss     : {test_loss:.4f}")
    print(f"\nModèle sauvegardé dans : {MODEL_SAVE}")
