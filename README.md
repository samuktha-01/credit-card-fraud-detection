# Credit Card Fraud Detection with Imbalanced Data

## 📌 Project Overview

This project develops a machine learning system to detect fraudulent credit card transactions using the Kaggle Credit Card Fraud Detection dataset.

The main challenge is the highly imbalanced nature of the dataset, where fraudulent transactions represent only a very small percentage of all transactions.

The project focuses on handling this imbalance and evaluating the model using precision, recall, F1-score, Average Precision, and Precision-Recall curves rather than relying on accuracy alone.

---

## 🎯 Problem Statement

Credit card fraud detection is a binary classification problem where each transaction must be classified as either:

- `0` → Legitimate transaction
- `1` → Fraudulent transaction

The dataset contains 284,807 transactions, but only 492 are fraudulent.

This creates a severe class imbalance, making accuracy an unreliable evaluation metric.

---

## 📊 Dataset

The project uses the **Credit Card Fraud Detection** dataset from Kaggle.

Dataset characteristics:

- Total transactions: **284,807**
- Legitimate transactions: **284,315**
- Fraudulent transactions: **492**
- Total features: **30**
- Target variable: `Class`

### Features

The dataset contains:

- `Time`
- `V1` to `V28`
- `Amount`
- `Class`

`V1` to `V28` are anonymized PCA-transformed features derived from the original transaction information.

The dataset is intentionally excluded from this GitHub repository because the CSV file is larger than GitHub's standard file-size limit.

---

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Imbalanced-learn
- XGBoost
- Matplotlib
- Jupyter Notebook
- Git & GitHub

---

## 🔄 Project Workflow

```text
Dataset
   ↓
Data Exploration
   ↓
Check Missing Values
   ↓
Separate Features and Target
   ↓
Train/Test Split
   ↓
Handle Class Imbalance
   ├── SMOTE
   └── Class Weighting
   ↓
XGBoost
   ↓
Predictions
   ↓
Precision / Recall / F1
   ↓
Precision-Recall Curve
   ↓
Average Precision
   ↓
Threshold Optimization