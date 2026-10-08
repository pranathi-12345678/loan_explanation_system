from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import joblib
import pandas as pd
import shap

from dotenv import load_dotenv
import os

from google import genai
from google.genai import types

import json


# ==================================================
# Load environment variables
# ==================================================

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file."
    )


# ==================================================
# Create Gemini client
# ==================================================

client = genai.Client(
    api_key=gemini_api_key
)


# ==================================================
# Create FastAPI application
# ==================================================

app = FastAPI()


# ==================================================
# Allow frontend to communicate with backend
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==================================================
# Load trained model and preprocessor
# ==================================================

rf_model = joblib.load(
    "backend/rf_model.pkl"
)

preprocessor = joblib.load(
    "backend/preprocessor.pkl"
)


# ==================================================
# Create SHAP explainer
# ==================================================

explainer = shap.TreeExplainer(
    rf_model
)


# ==================================================
# Load loan application data
# ==================================================

df = pd.read_csv(
    "data/loan_approval_dataset.csv"
)


# ==================================================
# Clean column names
# ==================================================

df.columns = df.columns.str.strip()


# ==================================================
# Clean loan status values
# ==================================================

df["loan_status"] = (
    df["loan_status"]
    .str.strip()
)


# ==================================================
# Recreate engineered features used during training
# ==================================================

df["TotalAssets"] = (
    df["residential_assets_value"]
    + df["commercial_assets_value"]
    + df["luxury_assets_value"]
    + df["bank_asset_value"]
)

df["LoanToIncome"] = (
    df["loan_amount"]
    / df["income_annum"]
)

df["AssetCoverage"] = (
    df["TotalAssets"]
    / df["loan_amount"]
)


# ==================================================
# Home endpoint
# ==================================================

@app.get("/")
def home():

    return {
        "message": "Loan Explanation System API is running"
    }


# ==================================================
# Model status endpoint
# ==================================================

@app.get("/model-status")
def model_status():

    return {
        "model_loaded": True,
        "preprocessor_loaded": True,
        "shap_loaded": True,
        "gemini_loaded": True
    }


# ==================================================
# Generate Gemini prompts
# ==================================================

def generate_prompts(decision, factors):

    factors_json = json.dumps(
        factors,
        indent=2
    )

    # ==================================================
    # Rejected application
    # ==================================================

    if decision == "Rejected":

        # --------------------------------------------------
        # Reason prompt
        # --------------------------------------------------

        reason_prompt = f"""
You are an AI loan explanation assistant.

The applicant's loan application was REJECTED.

For EACH factor provided below, write ONE simple explanation.

IMPORTANT LANGUAGE RULES:

1. Use VERY SIMPLE ENGLISH.
2. Write for a person who knows only basic English.
3. Use short and clear sentences.
4. Use common everyday words.
5. Avoid financial jargon and difficult words.
6. Explain each factor independently.
7. Do NOT compare one factor with another.
8. Do NOT combine factors.
9. Do NOT introduce any factor that is not provided.
10. Do NOT mention SHAP, machine learning, model, algorithm,
    prediction, or feature importance.
11. Do NOT say that a factor definitely caused the rejection.
12. Explain that the factor negatively affected the loan assessment.
13. Do NOT repeat the applicant's numerical value.
14. The applicant's actual value will be displayed separately.
15. Do NOT give recommendations.
16. Keep each explanation to ONE or TWO short sentences.
17. Do NOT use difficult financial words.
18. Return EXACTLY one explanation for EACH provided factor.

IMPORTANT:

Each explanation MUST be connected to the EXACT feature name provided.

Return ONLY valid JSON.

Use exactly this format:

[
  {{
    "feature": "exact feature name",
    "reason": "simple explanation"
  }}
]

The feature names must be copied EXACTLY from the input.

The factors are:

{factors_json}
"""


        # --------------------------------------------------
        # Suggestion prompt
        # --------------------------------------------------

        suggestion_prompt = f"""
You are a loan guidance assistant.

The applicant's loan application was REJECTED.

For EACH factor provided below, give ONE practical suggestion.

IMPORTANT RULES:

1. Use VERY SIMPLE ENGLISH.
2. Write for a person who knows only basic English.
3. Use short and clear sentences.
4. Use common everyday words.
5. Each suggestion must directly relate to its EXACT factor.
6. Do NOT give suggestions about any other factor.
7. Do NOT compare the factors.
8. Do NOT combine the factors.
9. Do NOT use technical terms such as SHAP, machine learning,
   model, algorithm, or feature importance.
10. Do NOT promise that following a suggestion will guarantee approval.
11. Do NOT say that changing a factor will definitely result in approval.
12. For cibil_score, suggest improving credit history through
    responsible payment habits and managing existing debt.
13. For LoanToIncome, suggest considering a loan amount that is
    more manageable compared with income.
14. For loan_term, suggest discussing different loan-period
    options with the bank.
15. Keep each suggestion to ONE short sentence.
16. Return EXACTLY one suggestion for EACH provided factor.

IMPORTANT:

Each suggestion MUST be connected to the EXACT feature name provided.

Return ONLY valid JSON.

Use exactly this format:

[
  {{
    "feature": "exact feature name",
    "suggestion": "simple practical suggestion"
  }}
]

The feature names must be copied EXACTLY from the input.

The factors are:

{factors_json}
"""

        return (
            reason_prompt,
            suggestion_prompt
        )


    # ==================================================
    # Approved application
    # ==================================================

    else:

        reason_prompt = f"""
You are an AI loan explanation assistant.

The applicant's loan application was APPROVED.

For EACH factor provided below, write ONE simple explanation.

IMPORTANT LANGUAGE RULES:

1. Use VERY SIMPLE ENGLISH.
2. Write for a person who knows only basic English.
3. Use short and clear sentences.
4. Use common everyday words.
5. Avoid financial jargon and difficult words.
6. Explain each factor independently.
7. Do NOT compare one factor with another.
8. Do NOT combine factors.
9. Do NOT introduce any factor that is not provided.
10. Do NOT mention SHAP, machine learning, model, algorithm,
    prediction, or feature importance.
11. Do NOT say that a factor definitely caused the approval.
12. Explain that the factor positively affected the loan assessment.
13. Do NOT repeat the applicant's numerical value.
14. The applicant's actual value will be displayed separately.
15. Do NOT give recommendations.
16. Keep each explanation to ONE or TWO short sentences.
17. Do NOT use difficult financial words.
18. Return EXACTLY one explanation for EACH provided factor.

IMPORTANT:

Each explanation MUST be connected to the EXACT feature name provided.

Return ONLY valid JSON.

Use exactly this format:

[
  {{
    "feature": "exact feature name",
    "reason": "simple explanation"
  }}
]

The feature names must be copied EXACTLY from the input.

The factors are:

{factors_json}
"""

        return (
            reason_prompt,
            None
        )


# ==================================================
# Application lookup and explanation
# ==================================================

@app.get("/application/{application_id}")
def get_application(application_id: int):

    # ==================================================
    # Find application using Application ID
    # ==================================================

    applicant = df[
        df["loan_id"] == application_id
    ]


    # ==================================================
    # Application ID not found
    # ==================================================

    if applicant.empty:

        return {
            "status": "not_found",
            "message": "Application ID not found."
        }


    # ==================================================
    # Get applicant row
    # ==================================================

    row = applicant.iloc[0]


    # ==================================================
    # Prepare applicant data for model
    # ==================================================

    applicant_features = applicant.drop(
        columns=[
            "loan_id",
            "loan_status"
        ]
    )


    # ==================================================
    # Apply trained preprocessor
    # ==================================================

    applicant_transformed = (
        preprocessor.transform(
            applicant_features
        )
    )


    # ==================================================
    # Random Forest prediction
    # ==================================================

    prediction = rf_model.predict(
        applicant_transformed
    )[0]


    # Convert prediction to readable decision

    decision = (
        "Approved"
        if prediction == 1
        else "Rejected"
    )


    # ==================================================
    # Calculate SHAP values
    # ==================================================

    shap_result = explainer.shap_values(
        applicant_transformed
    )


    # SHAP values for Approved class

    shap_approved = (
        shap_result[0, :, 1]
    )


    # ==================================================
    # Get transformed feature names
    # ==================================================

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )


    # ==================================================
    # Create SHAP DataFrame
    # ==================================================

    shap_df = pd.DataFrame(
        {
            "feature": feature_names,
            "shap_value": shap_approved
        }
    )


    # ==================================================
    # Select factors according to decision
    # ==================================================

    if decision == "Approved":

        # Positive SHAP values helped move
        # the decision toward Approved

        selected_factors = shap_df[
            shap_df["shap_value"] > 0
        ].copy()

    else:

        # Negative SHAP values moved
        # the decision away from Approved

        selected_factors = shap_df[
            shap_df["shap_value"] < 0
        ].copy()


    # ==================================================
    # Rank factors by absolute SHAP value
    # ==================================================

    selected_factors[
        "absolute_shap"
    ] = (
        selected_factors[
            "shap_value"
        ].abs()
    )


    selected_factors = (
        selected_factors
        .sort_values(
            "absolute_shap",
            ascending=False
        )
        .head(3)
        .copy()
    )


    # ==================================================
    # Remove preprocessing prefixes
    # ==================================================

    selected_factors[
        "original_feature"
    ] = (
        selected_factors[
            "feature"
        ]
        .str.replace(
            "numeric__",
            "",
            regex=False
        )
        .str.replace(
            "categorical__",
            "",
            regex=False
        )
    )


    # ==================================================
    # Get applicant's actual value
    # ==================================================

    def get_applicant_value(feature):

        # Direct numerical feature

        if feature in applicant.columns:

            return row[feature]


        # One-hot encoded education feature

        if feature.startswith(
            "education_"
        ):

            return row[
                "education"
            ]


        # One-hot encoded employment feature

        if feature.startswith(
            "self_employed_"
        ):

            return row[
                "self_employed"
            ]


        return None


    selected_factors[
        "applicant_value"
    ] = (
        selected_factors[
            "original_feature"
        ]
        .apply(
            get_applicant_value
        )
    )


    # ==================================================
    # Prepare factors for Gemini
    # ==================================================

    factors = selected_factors[
        [
            "original_feature",
            "applicant_value",
            "shap_value"
        ]
    ].rename(
        columns={
            "original_feature": "feature"
        }
    )


    factors_output = (
        factors
        .to_dict(
            orient="records"
        )
    )


    # ==================================================
    # Generate Gemini prompts
    # ==================================================

    reason_prompt, suggestion_prompt = (
        generate_prompts(
            decision,
            factors_output
        )
    )


    # ==================================================
    # Generate Gemini reasons
    # ==================================================

    reason_response = (
        client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=reason_prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=400
            )
        )
    )


    # ==================================================
    # Convert Gemini reason JSON to Python
    # ==================================================

    try:

        reasons = json.loads(
            reason_response.text
        )

    except json.JSONDecodeError:

        reasons = []


    # ==================================================
    # Generate suggestions only for rejected
    # ==================================================

    suggestions = None


    if decision == "Rejected":

        suggestion_response = (
            client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=suggestion_prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=400
                )
            )
        )


        # --------------------------------------------------
        # Convert Gemini suggestion JSON to Python
        # --------------------------------------------------

        try:

            suggestions = json.loads(
                suggestion_response.text
            )

        except json.JSONDecodeError:

            suggestions = []


    # ==================================================
    # Final API response
    # ==================================================

    return {

        "status": "success",

        "application_id": application_id,

        "decision": decision,

        "factors": factors_output,

        "reasons": reasons,

        "suggestions": suggestions
    }