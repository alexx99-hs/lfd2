# -*- coding: utf-8 -*-
"""irony stage 3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IPzmLMjPlaF8zl9Ia0azOMow6ax1dTf1
"""

# prompt: import my dataset from my local

from google.colab import files
uploaded = files.upload()
import pandas as pd
import io

# prompt: import my glove from mydrive

from google.colab import drive
drive.mount('/content/drive')

# Assuming your GloVe file is in 'My Drive/glove_data' and named 'glove.6B.50d.txt'
glove_file_path = '/content/drive/MyDrive/1b/glove.6B.100d.txt'  # Update with your actual path

# Now you can use glove_file_path to load your GloVe embeddings
# Example using Gensim:
# from gensim.scripts.glove2word2vec import glove2word2vec
# glove2word2vec(glove_file_path, 'glove_word2vec.txt')

# Import NumPy
import numpy as np

# Example using a different method to load the file directly:
embeddings_index = {}
with open(glove_file_path, encoding='utf8') as f:
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs

# Print the number of loaded words
print('Loaded %s word vectors.' % len(embeddings_index))



# Download only the 100-dimensional GloVe file
!wget http://nlp.stanford.edu/data/glove.6B.zip

# Unzip only the required file (100d embeddings)
!unzip -j glove.6B.zip glove.6B.100d.txt

import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
import numpy as np

# Step 1: Load Preprocessed Data
# Replace these filenames with your actual preprocessed data files
train_df = pd.read_csv('merged_train_set.csv')
test_df = pd.read_csv('test_fully_preprocessed.csv')

# Split train data into train and validation sets
X_train, X_val, y_train, y_val = train_test_split(
    train_df['tweet'], train_df['label'], test_size=0.2, random_state=42)

X_test = test_df['tweet']
y_test = test_df['label']

# Step 2: Tokenize and Pad Sequences
max_words = 10000  # Limit vocabulary size
max_len = 100  # Max tweet length

tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(X_train)

# Convert text to sequences and pad them
X_train_seq = tokenizer.texts_to_sequences(X_train)
X_val_seq = tokenizer.texts_to_sequences(X_val)
X_test_seq = tokenizer.texts_to_sequences(X_test)

X_train_pad = pad_sequences(X_train_seq, maxlen=max_len, padding='post')
X_val_pad = pad_sequences(X_val_seq, maxlen=max_len, padding='post')
X_test_pad = pad_sequences(X_test_seq, maxlen=max_len, padding='post')

# Step 3: Load GloVe Embeddings
embedding_dim = 100
embedding_index = {}

# Ensure you have downloaded `glove.6B.100d.txt`
glove_file = 'glove.6B.100d.txt'
with open(glove_file, 'r', encoding='utf-8') as f:
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embedding_index[word] = coefs

# Create embedding matrix
vocab_size = len(tokenizer.word_index) + 1
embedding_matrix = np.zeros((vocab_size, embedding_dim))

for word, i in tokenizer.word_index.items():
    if i < max_words:
        embedding_vector = embedding_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector

# Step 4: Build the LSTM Model
model = Sequential([
    Embedding(input_dim=vocab_size,
              output_dim=embedding_dim,
              weights=[embedding_matrix],
              input_length=max_len,
              trainable=False),  # Use static embeddings
    LSTM(128, dropout=0.2, recurrent_dropout=0.2),  # Single LSTM layer
    Dense(1, activation='sigmoid')  # Binary classification
])

model.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

model.summary()

# Step 5: Train the Model
history = model.fit(
    X_train_pad, y_train,
    validation_data=(X_val_pad, y_val),
    epochs=10,
    batch_size=64,
    verbose=1
)

# Step 6: Evaluate the Model
loss, accuracy = model.evaluate(X_test_pad, y_test, verbose=1)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

# Step 7: Save the Model
model.save('simple_lstm_glove_model.h5')
print("LSTM model saved as 'simple_lstm_glove_model.h5'.")

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Bidirectional, LSTM, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import numpy as np

# Step 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Step 2: Load Preprocessed Data
train_df = pd.read_csv('merged_train_set.csv')
test_df = pd.read_csv('test_fully_preprocessed.csv')

# Split train data into train and validation sets
X_train, X_val, y_train, y_val = train_test_split(
    train_df['tweet'], train_df['label'], test_size=0.2, random_state=42)

X_test = test_df['tweet']
y_test = test_df['label']

# Step 3: Tokenize and Pad Sequences
max_words = 10000  # Limit vocabulary size
max_len = 100  # Max tweet length

tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(X_train)

X_train_seq = tokenizer.texts_to_sequences(X_train)
X_val_seq = tokenizer.texts_to_sequences(X_val)
X_test_seq = tokenizer.texts_to_sequences(X_test)

X_train_pad = pad_sequences(X_train_seq, maxlen=max_len, padding='post')
X_val_pad = pad_sequences(X_val_seq, maxlen=max_len, padding='post')
X_test_pad = pad_sequences(X_test_seq, maxlen=max_len, padding='post')

# Step 4: Apply SMOTE for Oversampling
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_pad, y_train)

# Check class distribution after oversampling
print("Class distribution after SMOTE:")
print(pd.Series(y_train_resampled).value_counts())

# Step 5: Load GloVe Embeddings
embedding_dim = 100
embedding_index = {}

glove_file = '/content/drive/MyDrive/1b/glove.6B.100d.txt'

# Load GloVe embeddings
with open(glove_file, 'r', encoding='utf-8') as f:
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embedding_index[word] = coefs

# Create embedding matrix
vocab_size = len(tokenizer.word_index) + 1
embedding_matrix = np.zeros((vocab_size, embedding_dim))

for word, i in tokenizer.word_index.items():
    if i < max_words:
        embedding_vector = embedding_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector

# Step 6: Build the LSTM Model
model = Sequential([
    Embedding(input_dim=vocab_size,
              output_dim=embedding_dim,
              weights=[embedding_matrix],
              input_length=max_len,
              trainable=True),  # Allow fine-tuning of embeddings
    Bidirectional(LSTM(128, dropout=0.3, recurrent_dropout=0.3)),  # Bidirectional LSTM
    Dense(64, activation='relu'),
    Dense(1, activation='sigmoid')  # Binary classification
])

# Compile the model with a lower learning rate
model.compile(
    loss='binary_crossentropy',
    optimizer=Adam(learning_rate=0.0001),
    metrics=['accuracy']
)

model.summary()

# Step 7: Train the Model with Early Stopping
early_stopping = EarlyStopping(
    monitor='val_accuracy', patience=3, restore_best_weights=True
)

history = model.fit(
    X_train_resampled, y_train_resampled,
    validation_data=(X_val_pad, y_val),
    epochs=10,
    batch_size=64,
    callbacks=[early_stopping],
    verbose=1
)

# Step 8: Evaluate the Model
loss, accuracy = model.evaluate(X_test_pad, y_test, verbose=1)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

# Generate predictions
y_pred = (model.predict(X_test_pad) > 0.5).astype('int32')

# Step 9: Classification Evaluation
print("Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=['Non-Ironic', 'Ironic']))

# Step 10: Save the Model
model.save('/content/drive/MyDrive/1b/final_lstm_glove_model_with_smote.keras')
print("LSTM model saved as 'final_lstm_glove_model_with_smote.keras'.")



import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Bidirectional, LSTM, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import numpy as np

# Step 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Step 2: Load Preprocessed Data
train_df = pd.read_csv('merged_train_set.csv')
test_df = pd.read_csv('test_fully_preprocessed.csv')

# Split train data into train and validation sets
X_train, X_val, y_train, y_val = train_test_split(
    train_df['tweet'], train_df['label'], test_size=0.2, random_state=42)

X_test = test_df['tweet']
y_test = test_df['label']

# Step 3: Tokenize and Pad Sequences
max_words = 10000  # Limit vocabulary size
max_len = 100  # Max tweet length

tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(X_train)

X_train_seq = tokenizer.texts_to_sequences(X_train)
X_val_seq = tokenizer.texts_to_sequences(X_val)
X_test_seq = tokenizer.texts_to_sequences(X_test)

X_train_pad = pad_sequences(X_train_seq, maxlen=max_len, padding='post')
X_val_pad = pad_sequences(X_val_seq, maxlen=max_len, padding='post')
X_test_pad = pad_sequences(X_test_seq, maxlen=max_len, padding='post')

# Step 4: Apply SMOTE for Oversampling
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_pad, y_train)

# Check class distribution after oversampling
print("Class distribution after SMOTE:")
print(pd.Series(y_train_resampled).value_counts())

# Step 5: Load GloVe Embeddings
embedding_dim = 100
embedding_index = {}

glove_file = '/content/drive/MyDrive/1b/glove.6B.100d.txt'

# Load GloVe embeddings
with open(glove_file, 'r', encoding='utf-8') as f:
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embedding_index[word] = coefs

# Create embedding matrix
vocab_size = len(tokenizer.word_index) + 1
embedding_matrix = np.zeros((vocab_size, embedding_dim))

for word, i in tokenizer.word_index.items():
    if i < max_words:
        embedding_vector = embedding_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector

# Step 6: Build the LSTM Model
model = Sequential([
    Embedding(input_dim=vocab_size,
              output_dim=embedding_dim,
              weights=[embedding_matrix],
              input_length=max_len,
              trainable=True),  # Allow fine-tuning of embeddings
    Bidirectional(LSTM(128, return_sequences=True, dropout=0.3, recurrent_dropout=0.3)),
    Bidirectional(LSTM(128, dropout=0.3, recurrent_dropout=0.3)),
    Dense(64, activation='relu'),
    Dense(1, activation='sigmoid')
])

# Compile the model with a lower learning rate
model.compile(
    loss='binary_crossentropy',
    optimizer=Adam(learning_rate=0.0001),
    metrics=['accuracy']
)

model.summary()

# Step 7: Train the Model with Early Stopping
early_stopping = EarlyStopping(
    monitor='val_accuracy', patience=3, restore_best_weights=True
)

history = model.fit(
    X_train_resampled, y_train_resampled,
    validation_data=(X_val_pad, y_val),
    epochs=20,
    batch_size=64,
    callbacks=[early_stopping],
    verbose=1
)

# Step 8: Evaluate the Model
loss, accuracy = model.evaluate(X_test_pad, y_test, verbose=1)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

# Generate predictions
y_pred = (model.predict(X_test_pad) > 0.5).astype('int32')

# Step 9: Classification Evaluation
print("Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=['Non-Ironic', 'Ironic']))

# Step 10: Save the Model
model.save('/content/drive/MyDrive/1b/final_lstm_glove_model_with_smote.keras')
print("LSTM model saved as 'final_lstm_glove_model_with_smote.keras'.")