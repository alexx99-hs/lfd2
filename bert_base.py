# -*- coding: utf-8 -*-
"""bert-base.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1FzoWs57m3vtbRqxJAfiFlA-9Z0yIlgjK
"""

from google.colab import files
uploaded = files.upload()
import pandas as pd
import io

from huggingface_hub import login
login("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")

!pip install fsspec==2024.10.0

# Step 1: Install Required Libraries
!pip install transformers datasets accelerate huggingface-hub -q

# Step 2: Import Libraries
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset, DatasetDict
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pandas as pd

# Step 3: Check GPU Availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Step 4: Load Preprocessed Data
train_file = '/content/merged_train_set.csv'
test_file = '/content/test_fully_preprocessed.csv'

train_df = pd.read_csv(train_file)
test_df = pd.read_csv(test_file)

# Split into train and validation sets
train_data, val_data = train_test_split(train_df, test_size=0.2, random_state=42)

# Convert to Hugging Face Dataset
def convert_to_dataset(df, text_column, label_column):
    return Dataset.from_pandas(df[[text_column, label_column]].rename(columns={text_column: "text", label_column: "label"}))

train_dataset = convert_to_dataset(train_data, text_column="tweet", label_column="label")
val_dataset = convert_to_dataset(val_data, text_column="tweet", label_column="label")
test_dataset = convert_to_dataset(test_df, text_column="tweet", label_column="label")

datasets = DatasetDict({
    "train": train_dataset,
    "validation": val_dataset,
    "test": test_dataset,
})

# Step 5: Load Pretrained BERT Model and Tokenizer
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2).to(device)

# Step 6: Tokenize the Data
def tokenize_function(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=256)

tokenized_datasets = datasets.map(tokenize_function, batched=True)

# Remove unnecessary columns and set PyTorch format
tokenized_datasets = tokenized_datasets.remove_columns(["text"])
tokenized_datasets.set_format("torch")

# Step 7: Define Metric for Evaluation
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = torch.argmax(torch.tensor(logits), dim=-1)
    acc = accuracy_score(labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="binary")
    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

# Step 8: Define Training Arguments
training_args = TrainingArguments(
    output_dir="./bert_results",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    num_train_epochs=5,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    fp16=True  # Mixed precision for faster training
)

# Step 9: Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

# Step 10: Train the Model
trainer.train()

# Step 11: Evaluate on Test Set
print("Evaluating on Test Set...")
test_results = trainer.evaluate(tokenized_datasets["test"])
print(test_results)

# Step 12: Save the Fine-Tuned Model
model.save_pretrained("/content/drive/MyDrive/fine_tuned_bert")
tokenizer.save_pretrained("/content/drive/MyDrive/fine_tuned_bert")
print("Fine-tuned model saved at: /content/drive/MyDrive/fine_tuned_bert")