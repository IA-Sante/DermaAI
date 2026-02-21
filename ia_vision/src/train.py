"""
train.py – Entraînement du modèle DermaAI en deux phases.

Phase 1 : Feature extraction  – base MobileNetV2 gelée, 10 époques.
Phase 2 : Fine-tuning          – 30 dernières couches dégelées, 10 époques.

Usage:
    python train.py --splits_dir data/splits --models_dir models \
                    --epochs1 10 --epochs2 10 --batch_size 32
"""

import argparse
import os

import tensorflow as tf

from data_loader import get_datasets
from model import build_model, unfreeze_top_layers


def train(splits_dir: str = "data/splits",
          models_dir: str = "models",
          epochs1: int = 10,
          epochs2: int = 10,
          batch_size: int = 32) -> tf.keras.callbacks.History:
    """
    Entraîne le modèle en deux phases et le sauvegarde.

    Args:
        splits_dir:  Dossier contenant train.csv / val.csv / test.csv.
        models_dir:  Dossier de destination pour le modèle sauvegardé.
        epochs1:     Nombre d'époques pour la phase 1 (feature extraction).
        epochs2:     Nombre d'époques pour la phase 2 (fine-tuning).
        batch_size:  Taille des batches.

    Returns:
        Historique Keras de la phase 2.
    """
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "dermai_cnn.h5")

    train_ds, val_ds, test_ds = get_datasets(splits_dir, batch_size)

    # ------------------------------------------------------------------
    # Phase 1 – Feature extraction
    # ------------------------------------------------------------------
    print("\n=== Phase 1 : Feature extraction ===")
    model = build_model(learning_rate=1e-3)

    callbacks_p1 = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=3, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=2, verbose=1
        ),
    ]

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs1,
        callbacks=callbacks_p1,
    )

    # ------------------------------------------------------------------
    # Phase 2 – Fine-tuning
    # ------------------------------------------------------------------
    print("\n=== Phase 2 : Fine-tuning ===")
    unfreeze_top_layers(model, num_layers=30, learning_rate=1e-5)

    callbacks_p2 = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=model_path,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, verbose=1
        ),
    ]

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs2,
        callbacks=callbacks_p2,
    )

    # ------------------------------------------------------------------
    # Évaluation finale sur le test set
    # ------------------------------------------------------------------
    print("\n=== Évaluation sur le test set ===")
    loss, acc = model.evaluate(test_ds)
    print(f"Test loss     : {loss:.4f}")
    print(f"Test accuracy : {acc:.4f}")

    # Sauvegarde finale (au cas où ModelCheckpoint n'a pas été déclenché)
    if not os.path.exists(model_path):
        model.save(model_path)
    print(f"Modèle sauvegardé dans {model_path}")

    return history


def main() -> None:
    """Point d'entrée CLI pour l'entraînement DermaAI en deux phases."""
    parser = argparse.ArgumentParser(
        description="Entraînement DermaAI (2 phases)"
    )
    parser.add_argument("--splits_dir", default="data/splits")
    parser.add_argument("--models_dir", default="models")
    parser.add_argument("--epochs1", type=int, default=10)
    parser.add_argument("--epochs2", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=32)
    args = parser.parse_args()

    train(
        splits_dir=args.splits_dir,
        models_dir=args.models_dir,
        epochs1=args.epochs1,
        epochs2=args.epochs2,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
