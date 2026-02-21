"""
model.py – Architecture MobileNetV2 pour la classification de lésions cutanées.

7 classes HAM10000 : akiec, bcc, bkl, df, mel, nv, vasc.
"""

from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam

NUM_CLASSES = 7
IMG_SIZE = (224, 224)
INPUT_SHAPE = (*IMG_SIZE, 3)


def build_model(num_classes: int = NUM_CLASSES,
                input_shape: tuple = INPUT_SHAPE,
                learning_rate: float = 1e-3) -> models.Model:
    """
    Construit et compile un modèle basé sur MobileNetV2.

    Phase 1 – feature extraction : base gelée, seule la tête est entraînée.
    Pour la phase 2 (fine-tuning), appeler ``unfreeze_top_layers`` puis
    recompiler avec un learning rate plus faible.

    Args:
        num_classes:    Nombre de classes de sortie.
        input_shape:    Forme de l'entrée (H, W, C).
        learning_rate:  Taux d'apprentissage initial.

    Returns:
        Modèle Keras compilé.
    """
    base = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False  # gelé pour la phase 1

    inputs = layers.Input(shape=input_shape, name="input_image")
    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    x = layers.Dense(256, activation="relu", name="fc1")(x)
    x = layers.Dropout(0.3, name="dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = models.Model(inputs, outputs, name="DermaAI_MobileNetV2")
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def unfreeze_top_layers(model: models.Model,
                        num_layers: int = 30,
                        learning_rate: float = 1e-5) -> None:
    """
    Dégèle les `num_layers` dernières couches de la base pour le fine-tuning
    (phase 2) et recompile le modèle.

    Args:
        model:        Modèle retourné par ``build_model``.
        num_layers:   Nombre de couches à dégeler depuis la fin de la base.
        learning_rate: Taux d'apprentissage réduit pour le fine-tuning.
    """
    base = model.get_layer("mobilenetv2_1.00_224")
    base.trainable = True

    for layer in base.layers[:-num_layers]:
        layer.trainable = False

    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )


if __name__ == "__main__":
    m = build_model()
    m.summary()
