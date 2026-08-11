"""
Trains a small feedforward DNN to classify mood from HRV features.

Reads the same CSV your Flask app writes to (heart_mood_dataset.csv),
fits a softmax classifier, and saves three artifacts:
  - mood_model.keras       the trained network
  - mood_scaler.pkl        feature scaler (must be reused at inference time)
  - mood_label_encoder.pkl maps between mood strings and class indices

Run this offline, on your laptop or the Pi, whenever you've collected
more labeled data and want to retrain:
    python3 train_mood_model.py
"""

import sys
import numpy as np
import pandas as pd
import joblib
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
DATASET_FILE = "heart_mood_dataset.csv"

# These must exactly match the columns HeartRateEngine.get_features() produces,
# in the same order, minus 'timestamp' and 'label'.
FEATURE_COLUMNS = [
    "mean_hr", "std_hr", "mean_rr", "sdnn",
    "rmssd"
]

MIN_ROWS_TO_TRAIN = 10          # below this, a DNN will just memorize noise
MIN_ROWS_PER_CLASS_WARNING = 3  # heads-up if any mood is underrepresented


def load_dataset():
    df = pd.read_csv(DATASET_FILE)
    missing_cols = [c for c in FEATURE_COLUMNS + ["label"] if c not in df.columns]
    if missing_cols:
        sys.exit(
            f"Dataset is missing columns: {missing_cols}. "
            f"Make sure you're using the updated Flask app that logs all HRV features."
        )

    df = df.dropna(subset=FEATURE_COLUMNS + ["label"])

    if len(df) < MIN_ROWS_TO_TRAIN:
        sys.exit(
            f"Only {len(df)} labeled rows in {DATASET_FILE} -- need at least "
            f"{MIN_ROWS_TO_TRAIN} to train something meaningful. Keep collecting "
            f"data with the mood buttons and re-run this script later."
        )

    counts = df["label"].value_counts()
    print("Rows per mood label:")
    print(counts.to_string())
    thin_classes = counts[counts < MIN_ROWS_PER_CLASS_WARNING]
    if not thin_classes.empty:
        print(
            f"\nHeads up: these labels have fewer than {MIN_ROWS_PER_CLASS_WARNING} "
            f"samples, the model will likely be weak on them:\n{thin_classes.to_string()}\n"
        )

    return df


def build_model(num_features, num_classes):
    # Small on purpose: 8 input features and (presumably) a few hundred rows
    # at most doesn't support a deep network -- it would just overfit.
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(num_features,)),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.3),  # helps prevent overfitting on a small dataset
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(num_classes, activation="softmax"),
    ])
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",  # labels are integers, not one-hot
        metrics=["accuracy"],
    )
    return model


def main():
    df = load_dataset()

    X = df[FEATURE_COLUMNS].values

    # Encode string labels ("Calm", "Happy", ...) as integers 0..N-1.
    # We save this encoder so inference code can map predictions back to names.
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["label"].values)
    num_classes = len(label_encoder.classes_)
    print(f"\nMood classes: {list(label_encoder.classes_)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features to zero mean / unit variance. Fit ONLY on training data
    # to avoid leaking test-set information, then apply the same transform
    # to both splits. This exact scaler gets saved and reused at inference --
    # never fit a new one on live data, or predictions will be wrong.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = build_model(num_features=X.shape[1], num_classes=num_classes)
    model.summary()

    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=15, restore_best_weights=True
    )

    history = model.fit(
        X_train_scaled, y_train,
        validation_data=(X_test_scaled, y_test),
        epochs=200,
        batch_size=16,
        callbacks=[early_stop],
        verbose=2,
    )

    test_loss, test_acc = model.evaluate(X_test_scaled, y_test, verbose=0)
    print(f"\nFinal test accuracy: {test_acc:.2%}")

    # Save everything inference will need: the model, the scaler, and the
    # label encoder. All three travel together -- a model without the
    # matching scaler will produce garbage predictions.
    model.save("mood_model.keras")
    joblib.dump(scaler, "mood_scaler.pkl")
    joblib.dump(label_encoder, "mood_label_encoder.pkl")
    print(
        "\nSaved mood_model.keras, mood_scaler.pkl, mood_label_encoder.pkl"
    )


if __name__ == "__main__":
    main()
