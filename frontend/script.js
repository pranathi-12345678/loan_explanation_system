// =========================================
// Backend API URL
// =========================================

const API_URL = "http://127.0.0.1:8000";


// =========================================
// Check application
// =========================================

async function checkApplication() {

    // Get elements from the page

    const applicationInput =
        document.getElementById("applicationId");

    const checkButton =
        document.getElementById("checkButton");

    const loading =
        document.getElementById("loading");

    const errorMessage =
        document.getElementById("errorMessage");

    const resultSection =
        document.getElementById("resultSection");


    // Get Application ID

    const applicationId =
        applicationInput.value.trim();


    // =========================================
    // Validate Application ID
    // =========================================

    if (!applicationId) {

        showError(
            "Please enter your Application ID."
        );

        return;
    }


    // =========================================
    // Reset previous results
    // =========================================

    errorMessage.classList.add("hidden");

    resultSection.classList.add("hidden");

    loading.classList.remove("hidden");

    checkButton.disabled = true;


    try {

        // =====================================
        // Call FastAPI backend
        // =====================================

        const response = await fetch(
            `${API_URL}/application/${applicationId}`
        );


        // =====================================
        // Convert response to JSON
        // =====================================

        const data = await response.json();


        // =====================================
        // Hide loading
        // =====================================

        loading.classList.add("hidden");

        checkButton.disabled = false;


        // =====================================
        // Application not found
        // =====================================

        if (data.status === "not_found") {

            showError(
                "❌ Application ID not found. Please check your Application ID and try again."
            );

            return;
        }


        // =====================================
        // Check for unexpected backend error
        // =====================================

        if (!response.ok) {

            showError(
                "Something went wrong. Please try again."
            );

            return;
        }


        // =====================================
        // Display application result
        // =====================================

        displayResult(data);


    } catch (error) {

        // =====================================
        // Backend connection error
        // =====================================

        loading.classList.add("hidden");

        checkButton.disabled = false;

        showError(
            "Unable to connect to the loan service. Please make sure the backend is running."
        );

        console.error(
            "Backend connection error:",
            error
        );
    }
}


// =========================================
// Display complete result
// =========================================

function displayResult(data) {

    const resultSection =
        document.getElementById("resultSection");

    const decisionElement =
        document.getElementById("decision");


    // =========================================
    // Display decision
    // =========================================

    decisionElement.textContent =
        data.decision.toUpperCase();


    // Remove previous decision classes

    decisionElement.classList.remove(
        "approved",
        "rejected"
    );


    // Add correct decision class

    if (data.decision === "Approved") {

        decisionElement.classList.add(
            "approved"
        );

    } else {

        decisionElement.classList.add(
            "rejected"
        );
    }


    // =========================================
    // Display factors
    // =========================================

    displayFactors(
        data.factors
    );


    // =========================================
    // Display reasons
    // =========================================

    displayReasons(
        data.reasons
    );


    // =========================================
    // Display suggestions
    // =========================================

    displaySuggestions(
        data.suggestions
    );


    // =========================================
    // Show result section
    // =========================================

    resultSection.classList.remove(
        "hidden"
    );
}


// =========================================
// Display factors
// =========================================

function displayFactors(factors) {

    const container =
        document.getElementById(
            "factorsContainer"
        );


    // Clear previous factors

    container.innerHTML = "";


    // Create one card for each factor

    factors.forEach(
        (factor, index) => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "factor-card";


            // Convert technical feature name
            // into applicant-friendly name

            const displayName =
                getDisplayName(
                    factor.feature
                );


            card.innerHTML = `
                <h3>
                    ${index + 1}. ${displayName}
                </h3>

                <p class="factor-label">
                    Your value
                </p>

                <p class="factor-value">
                    ${formatValue(
                        factor.applicant_value,
                        factor.feature
                    )}
                </p>
            `;


            container.appendChild(
                card
            );
        }
    );
}


// =========================================
// Display reasons
// =========================================

function displayReasons(reasons) {

    const container =
        document.getElementById(
            "reasonsContainer"
        );


    // Clear previous reasons

    container.innerHTML = "";


    if (!reasons || reasons.length === 0) {

        return;
    }


    // =========================================
    // Match reason with factor
    // =========================================

    reasons.forEach(
        (item, index) => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "reason-card";


            const displayName =
                getDisplayName(
                    item.feature
                );


            card.innerHTML = `
                <strong>
                    ${index + 1}. ${displayName}
                </strong>

                <p>
                    ${item.reason}
                </p>
            `;


            container.appendChild(
                card
            );
        }
    );
}


// =========================================
// Display suggestions
// =========================================

function displaySuggestions(
    suggestions
) {

    const section =
        document.getElementById(
            "suggestionsSection"
        );

    const container =
        document.getElementById(
            "suggestionsContainer"
        );


    // Clear previous suggestions

    container.innerHTML = "";


    // =========================================
    // Approved applications have no suggestions
    // =========================================

    if (
        !suggestions ||
        suggestions.length === 0
    ) {

        section.classList.add(
            "hidden"
        );

        return;
    }


    // =========================================
    // Rejected application suggestions
    // =========================================

    section.classList.remove(
        "hidden"
    );


    suggestions.forEach(
        (item, index) => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "suggestion-card";


            const displayName =
                getDisplayName(
                    item.feature
                );


            card.innerHTML = `
                <strong>
                    ${index + 1}. ${displayName}
                </strong>

                <p>
                    ${item.suggestion}
                </p>
            `;


            container.appendChild(
                card
            );
        }
    );
}


// =========================================
// Convert technical feature names
// to applicant-friendly names
// =========================================

function getDisplayName(feature) {

    const names = {

        "cibil_score":
            "Credit Score",

        "loan_term":
            "Loan Period",

        "LoanToIncome":
            "Loan Amount Compared With Income",

        "AssetCoverage":
            "Asset Coverage",

        "TotalAssets":
            "Total Assets",

        "loan_amount":
            "Loan Amount",

        "income_annum":
            "Annual Income",

        "no_of_dependents":
            "Number of Dependents",

        "residential_assets_value":
            "Residential Assets",

        "commercial_assets_value":
            "Commercial Assets",

        "luxury_assets_value":
            "Luxury Assets",

        "bank_asset_value":
            "Bank Assets",

        "education_Graduate":
            "Education",

        "education_Not Graduate":
            "Education",

        "self_employed_Yes":
            "Employment",

        "self_employed_No":
            "Employment"
    };


    return (
        names[feature] ||
        feature
    );
}


// =========================================
// Format applicant values
// =========================================

function formatValue(
    value,
    feature
) {

    // Credit score

    if (
        feature === "cibil_score"
    ) {

        return Number(value).toFixed(0);
    }


    // Loan period

    if (
        feature === "loan_term"
    ) {

        return `${Number(value).toFixed(0)} years`;
    }


    // Loan-to-income

    if (
        feature === "LoanToIncome"
    ) {

        return Number(value).toFixed(2);
    }


    // Other numerical values

    if (
        typeof value === "number"
    ) {

        return Number(value).toLocaleString(
            "en-IN"
        );
    }


    return value;
}


// =========================================
// Show error message
// =========================================

function showError(message) {

    const errorMessage =
        document.getElementById(
            "errorMessage"
        );


    errorMessage.textContent =
        message;


    errorMessage.classList.remove(
        "hidden"
    );
}


// =========================================
// Allow Enter key to submit
// =========================================

document
    .getElementById("applicationId")
    .addEventListener(
        "keydown",
        function(event) {

            if (
                event.key === "Enter"
            ) {

                checkApplication();
            }
        }
    );