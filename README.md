# 🛡️ FraudGuard — Credit Card Fraud Detection with Imbalanced Data

An end-to-end machine learning system for detecting fraudulent credit card transactions using XGBoost, SMOTE, FastAPI, and SHAP Explainable AI. The project addresses the extreme class imbalance present in credit card fraud detection and evaluates the model using precision, recall, F1-score, Average Precision, and threshold analysis rather than relying on accuracy alone. The trained model is exposed through a FastAPI backend and integrated with an interactive web dashboard for transaction analysis, risk assessment, transaction monitoring, analytics, and explainable predictions.

## 📌 Project Overview

Credit card fraud detection is a binary classification problem where each transaction is classified as either legitimate or fraudulent. The dataset contains 284,807 transactions, of which only 492 are fraudulent. This extreme class imbalance makes accuracy a poor metric for evaluating fraud detection performance. To address this problem, the project uses SMOTE during model development and an optimized decision threshold to improve the balance between precision and recall. The trained XGBoost model is served through FastAPI, while the frontend provides an interactive dashboard for analyzing transactions and understanding model predictions using SHAP.

## ✨ Features

- 🤖 XGBoost fraud classifier
- ⚖️ SMOTE-based imbalance handling
- 🎯 Decision threshold optimization
- 🧠 SHAP Explainable AI
- 🔍 Transaction-level fraud analysis
- 📊 Fraud probability scoring
- 🚦 Risk-level classification
- 📋 Recent transaction monitoring
- 📈 Fraud distribution visualization
- 📊 Confusion matrix
- 📉 Precision, Recall and F1 visualization
- ⚡ FastAPI REST API
- 💻 Interactive HTML/CSS/JavaScript dashboard
- 📊 Chart.js visualizations

## 🎯 Problem Statement

Credit card fraud detection is a binary classification problem where the objective is to correctly distinguish legitimate transactions from fraudulent transactions. The major challenge is the severe class imbalance, with 284,315 legitimate transactions and only 492 fraudulent transactions. Fraud represents only a very small proportion of the dataset. Because of this imbalance, a model could achieve very high accuracy while still failing to detect a significant number of fraudulent transactions. Therefore, this project focuses on precision, recall, F1 Score, Average Precision, confusion matrix, precision-recall analysis, and decision threshold optimization.

## 📊 Dataset

The project uses the Credit Card Fraud Detection dataset from Kaggle.

| Metric | Value |
|---|---:|
| Total transactions | 284,807 |
| Legitimate transactions | 284,315 |
| Fraudulent transactions | 492 |
| Total features | 30 |
| Target variable | `Class` |

The dataset contains `Time`, `V1` to `V28`, `Amount`, and `Class`. The `V1` to `V28` variables are anonymized PCA-transformed features. `Class = 0` represents a legitimate transaction and `Class = 1` represents a fraudulent transaction.

> ⚠️ The dataset is not included in this repository. Download `creditcard.csv` from Kaggle and place it at `data/creditcard.csv`.

Dataset: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

## 🛠️ Technologies Used

### Machine Learning
- Python
- Pandas
- NumPy
- Scikit-learn
- Imbalanced-learn
- SMOTE
- XGBoost
- SHAP

### Backend
- FastAPI
- Uvicorn
- Pydantic

### Frontend
- HTML5
- CSS3
- JavaScript
- Chart.js

### Development
- Jupyter Notebook
- Git
- GitHub

## 🔄 Project Workflow

```text
Dataset
   ↓
Data Exploration
   ↓
Data Preprocessing
   ↓
Train/Test Split
   ↓
Handle Class Imbalance
   ↓
SMOTE
   ↓
XGBoost
   ↓
Predictions
   ↓
Model Evaluation
   ↓
Precision / Recall / F1
   ↓
Average Precision
   ↓
Threshold Optimization
   ↓
Trained Model
   ↓
FastAPI API
   ↓
SHAP Explanations
   ↓
Interactive Dashboard

