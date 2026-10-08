# Loan Decision Explanation System

An Explainable AI (XAI) web application that helps loan applicants understand the main factors associated with their loan decision.

The system combines a machine-learning loan decision model, SHAP explainability, and Gemini-generated natural-language explanations in a simple applicant-facing web portal.

---

## 📌 Project Overview

Traditional loan systems may return only a decision such as:

- Approved
- Rejected

This project adds an **explanation layer** on top of the loan decision system.

The applicant enters their **Application ID**, and the system:

1. Retrieves the applicant's existing loan application.
2. Uses a trained Random Forest model to obtain the decision.
3. Uses SHAP to identify the three most influential factors for that decision.
4. Generates simple explanations using Gemini.
5. Shows the applicant-friendly result through a web dashboard.
6. Provides practical suggestions only when the application is rejected.

The system is designed to explain a decision rather than replace the bank's loan-processing system.

---

## 🎯 Key Features

### Application ID Based Lookup

Applicants enter their Application ID instead of manually entering all their financial information.

### Loan Decision

The system displays whether the application is:

- **Approved**
- **Rejected**

### Explainable AI

SHAP is used to identify the main factors influencing the model's decision.

For an approved application, the system selects the strongest factors that positively affect the approved-class prediction.

For a rejected application, the system selects the strongest factors that negatively affect the approved-class prediction.

### Simple Applicant-Friendly Explanations

Gemini converts the selected technical factors into short explanations using simple English.

The applicant does not see:

- SHAP values
- Machine-learning terminology
- Model terminology
- Technical feature names

### Rejection Suggestions

Rejected applications receive practical suggestions related to the identified factors.

Approved applications do not receive suggestions.

### Applicant-Friendly Interface

The frontend provides:

- Application ID search
- Decision display
- Main factors
- Simple explanations
- Suggestions for rejected applications
- Responsive design

---

## 🏗️ System Architecture

```text
                    Applicant
                        │
                        ▼
              ┌───────────────────┐
              │   Web Frontend    │
              │  HTML/CSS/JavaScript
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │    FastAPI        │
              │     Backend       │
              └─────────┬─────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
       Loan Application      Random Forest
            Data                 Model
                                  │
                                  ▼
                               SHAP
                                  │
                                  ▼
                         Top 3 Influential
                             Factors
                                  │
                                  ▼
                              Gemini
                                  │
                                  ▼
                    Simple Explanation
                                  │
                                  ▼
                        Frontend Dashboard
