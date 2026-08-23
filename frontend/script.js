const analyzeBtn = document.getElementById("analyzeBtn");

const transactionInput =
    document.getElementById("transactionId");

const resultBox =
    document.getElementById("result");

const predictionText =
    document.getElementById("prediction");

const transactionNumber =
    document.getElementById("transactionNumber");

const probabilityText =
    document.getElementById("probability");

const riskLevel =
    document.getElementById("riskLevel");

const actualResult =
    document.getElementById("actualResult");


async function analyzeTransaction() {

    const rowNumber = transactionInput.value.trim();

    if (rowNumber === "") {
        alert("Please enter a transaction number.");
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";

    resultBox.className = "result loading";

    predictionText.textContent =
        "Analyzing Transaction...";

    transactionNumber.textContent = "-";
    probabilityText.textContent = "-";
    riskLevel.textContent = "-";
    actualResult.textContent = "-";


    try {

        const response = await fetch(
            `http://127.0.0.1:8000/transaction/${rowNumber}`
        );

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(
                data.error || "Transaction analysis failed"
            );
        }


        const percentage =
            data.fraud_probability * 100;


        transactionNumber.textContent =
            data.transaction_id;

        probabilityText.textContent =
            percentage.toFixed(4) + "%";

        riskLevel.textContent =
            data.risk_level;

        actualResult.textContent =
            data.actual_result;


        if (data.prediction === "FRAUD") {

            resultBox.className = "result fraud";

            predictionText.textContent =
                "🚨 FRAUD DETECTED";

        } else {

            resultBox.className = "result normal";

            predictionText.textContent =
                "✅ TRANSACTION IS NORMAL";
        }
// Load SHAP explanation
await loadShapExplanation(rowNumber);

    } catch (error) {

        console.error("API Error:", error);

        resultBox.className = "result error";

        predictionText.textContent =
            "❌ ERROR";

        probabilityText.textContent =
            error.message;

    }


    analyzeBtn.disabled = false;
    analyzeBtn.textContent =
        "Analyze Transaction";
}


analyzeBtn.addEventListener(
    "click",
    analyzeTransaction
);


transactionInput.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {
            analyzeTransaction();
        }

    }
);

// ================= ANALYTICS CHART =================

const chartCanvas =
    document.getElementById("fraudDistributionChart");


if (chartCanvas) {

    new Chart(chartCanvas, {

        type: "doughnut",

        data: {

            labels: [
                "Normal Transactions",
                "Fraud Transactions"
            ],

            datasets: [
                {
                    data: [
                        284315,
                        492
                    ]
                }
            ]

        },

        options: {

            responsive: true,

            plugins: {

                legend: {
                    position: "bottom"
                },

                tooltip: {
                    callbacks: {

                        label: function(context) {

                            const value =
                                context.raw;

                            const total =
                                context.dataset.data
                                .reduce(
                                    (a, b) => a + b,
                                    0
                                );

                            const percentage =
                                (
                                    value / total
                                ) * 100;

                            return `${context.label}: ${value.toLocaleString()} (${percentage.toFixed(2)}%)`;

                        }

                    }
                }

            }

        }

    });

}

// ================= MODEL PERFORMANCE CHART =================

const performanceCanvas =
    document.getElementById("performanceChart");


if (performanceCanvas) {

    new Chart(performanceCanvas, {

        type: "bar",

        data: {

            labels: [
                "Precision",
                "Recall",
                "F1 Score"
            ],

            datasets: [
                {
                    label: "Model Score",

                    data: [
                        97.53,
                        80.61,
                        88.27
                    ]
                }
            ]

        },

        options: {

            responsive: true,

            scales: {

                y: {

                    beginAtZero: true,

                    max: 100,

                    ticks: {
                        callback: function(value) {
                            return value + "%";
                        }
                    }

                }

            },

            plugins: {

                legend: {
                    display: false
                }

            }

        }

    });

}

// ================= SHAP EXPLANATION =================

async function loadShapExplanation(rowNumber) {

    const explanationSection =
        document.getElementById("explanationSection");

    const transactionElement =
        document.getElementById("explanationTransaction");

    const predictionElement =
        document.getElementById("explanationPrediction");

    const probabilityElement =
        document.getElementById("explanationProbability");

    const fraudFeatures =
        document.getElementById("fraudFeatures");

    const normalFeatures =
        document.getElementById("normalFeatures");


    // Show loading state

    explanationSection.style.display = "block";

    transactionElement.textContent = rowNumber;

    predictionElement.textContent = "Loading...";

    probabilityElement.textContent = "Loading...";

    fraudFeatures.innerHTML = "<p>Loading explanation...</p>";

    normalFeatures.innerHTML = "";


    try {

        // Call SHAP API

        const response = await fetch(
            `http://127.0.0.1:8000/explain/${rowNumber}`
        );


        if (!response.ok) {

            throw new Error(
                `API returned ${response.status}`
            );

        }


        const data = await response.json();


        // Check API error

        if (data.error) {

            throw new Error(data.error);

        }


        // ================= SUMMARY =================

        transactionElement.textContent =
            data.transaction_id;

        predictionElement.textContent =
            data.prediction;

        probabilityElement.textContent =
            `${(data.fraud_probability * 100).toFixed(4)}%`;


        // ================= SHAP VALUES =================

        const fraud = data.explanations.filter(
            item => item.shap_value > 0
        );

        const normal = data.explanations.filter(
            item => item.shap_value < 0
        );


        // Show only strongest impacts

        const topFraud =
            fraud
                .sort(
                    (a, b) =>
                        Math.abs(b.shap_value) -
                        Math.abs(a.shap_value)
                )
                .slice(0, 6);


        const topNormal =
            normal
                .sort(
                    (a, b) =>
                        Math.abs(b.shap_value) -
                        Math.abs(a.shap_value)
                )
                .slice(0, 6);


        // ================= DISPLAY FRAUD FEATURES =================

        fraudFeatures.innerHTML = "";


        if (topFraud.length === 0) {

            fraudFeatures.innerHTML =
                "<p>No strong fraud-driving features.</p>";

        } else {

            topFraud.forEach(item => {

                const row =
                    createShapFeature(
                        item,
                        "fraud"
                    );

                fraudFeatures.appendChild(row);

            });

        }


        // ================= DISPLAY NORMAL FEATURES =================

        normalFeatures.innerHTML = "";


        if (topNormal.length === 0) {

            normalFeatures.innerHTML =
                "<p>No strong normal-driving features.</p>";

        } else {

            topNormal.forEach(item => {

                const row =
                    createShapFeature(
                        item,
                        "normal"
                    );

                normalFeatures.appendChild(row);

            });

        }


    } catch (error) {

        console.error(
            "SHAP explanation error:",
            error
        );


        predictionElement.textContent =
            "Unavailable";

        probabilityElement.textContent =
            "-";


        fraudFeatures.innerHTML =
            `<p>Could not load SHAP explanation.</p>`;

        normalFeatures.innerHTML = "";

    }

}


// ================= CREATE SHAP FEATURE =================

function createShapFeature(item, type) {

    const container =
        document.createElement("div");

    container.className =
        "shap-feature";


    const header =
        document.createElement("div");

    header.className =
        "shap-feature-header";


    const featureName =
        document.createElement("span");

    featureName.className =
        "shap-feature-name";

    featureName.textContent =
        item.feature;


    const featureValue =
        document.createElement("span");

    featureValue.className =
        "shap-feature-value";


    const sign =
        item.shap_value >= 0
            ? "+"
            : "";


    featureValue.textContent =
        `${sign}${item.shap_value.toFixed(3)}`;


    header.appendChild(featureName);

    header.appendChild(featureValue);


    // ================= BAR =================

    const barContainer =
        document.createElement("div");

    barContainer.className =
        "shap-bar-container";


    const bar =
        document.createElement("div");

    bar.className =
        "shap-bar";


    // Scale bar based on SHAP magnitude

    const percentage =
        Math.min(
            Math.abs(item.shap_value) / 7.33 * 100,
            100
        );


    bar.style.width =
        `${percentage}%`;


    barContainer.appendChild(bar);


    container.appendChild(header);

    container.appendChild(barContainer);


    return container;

}