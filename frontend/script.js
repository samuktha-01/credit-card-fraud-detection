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

const resultExplanationBtn =
    document.getElementById("resultExplanationBtn");

const resultErrorNotice =
    document.getElementById("resultErrorNotice");

console.log("transactionNumber:", transactionNumber);
console.log("probabilityText:", probabilityText);
console.log("riskLevel:", riskLevel);
console.log("actualResult:", actualResult);


async function analyzeTransaction() {

    const rowNumber = transactionInput.value.trim();

    if (rowNumber === "") {
        alert("Please enter a transaction number.");
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";

    resultBox.className = "result loading";

    if (resultErrorNotice) {
        resultErrorNotice.style.display = "none";
        resultErrorNotice.textContent = "";
    }

    if (resultExplanationBtn) {
        resultExplanationBtn.style.display = "none";
    }

    // Hide old SHAP explanation when analyzing a new transaction
    const explanationSection =
        document.getElementById("explanationSection");

    if (explanationSection) {
        explanationSection.style.display = "none";
    }

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

        if (resultErrorNotice) {
            resultErrorNotice.style.display = "none";
            resultErrorNotice.textContent = "";
        }

        if (resultExplanationBtn) {
            resultExplanationBtn.style.display = "";
            resultExplanationBtn.onclick = function () {
                loadExplanationForTransaction(rowNumber);
            };
        }


        if (data.prediction === "FRAUD") {

            resultBox.className = "result fraud";

            predictionText.textContent =
                "🚨 FRAUD DETECTED";

        } else {

            resultBox.className = "result normal";

            predictionText.textContent =
                "✅ TRANSACTION IS NORMAL";
        }

        // Automatically synchronize recent transactions history and summary counters
        try {
            await loadRecentTransactions();
        } catch (historyErr) {
            console.warn("Could not update transaction history:", historyErr);
        }


    } catch (error) {

        console.error("API Error:", error);

        resultBox.className = "result error";

        predictionText.textContent =
            "❌ Transaction Analysis Failed";

        if (resultErrorNotice) {
            resultErrorNotice.textContent =
                error.message || "Unable to analyze transaction. Please check the transaction number.";
            resultErrorNotice.style.display = "block";
        }

        probabilityText.textContent = "-";
        transactionNumber.textContent = "-";
        riskLevel.textContent = "-";
        actualResult.textContent = "-";

        if (resultExplanationBtn) {
            resultExplanationBtn.style.display = "none";
        }

    }


    analyzeBtn.disabled = false;
    analyzeBtn.textContent =
        "Analyze Transaction";
}

async function loadExplanationForTransaction(rowNumber) {

    try {

        const response = await fetch(
            `http://127.0.0.1:8000/explain/${rowNumber}`
        );

        const data = await response.json();

        if (!response.ok || data.error) {

            throw new Error(
                data.error ||
                "Unable to load explanation"
            );

        }

        const explanationSection =
            document.getElementById(
                "explanationSection"
            );

        if (!explanationSection) {
            throw new Error(
                "Explanation section not found"
            );
        }

        const explanations = Array.isArray(data.explanations) ? data.explanations : [];

        const fraudFeatures =
            explanations.filter(
                item =>
                    item && item.direction === "FRAUD"
            );

        const normalFeatures =
            explanations.filter(
                item =>
                    item && item.direction === "NORMAL"
            );

        // Dynamically compute the maximum absolute SHAP value for this transaction
        let maxShap = 0;
        for (const item of explanations) {
            const val = Math.abs(Number(item.shap_value) || 0);
            if (val > maxShap) {
                maxShap = val;
            }
        }
        // Avoid division by zero
        if (maxShap <= 0) {
            maxShap = 1;
        }


        explanationSection.style.display =
            "block";


        explanationSection.innerHTML = `

            <div class="section-heading">

                <div>

                    <h2>
                        🔍 Why Was This Transaction
                        Classified This Way?
                    </h2>

                    <p>
                        <strong>
                            Transaction #${rowNumber}
                        </strong>
                    </p>

                    <p>
                        SHAP shows which features
                        pushed the model toward
                        FRAUD or NORMAL.
                    </p>

                </div>

            </div>


            <div class="explanation-grid">


                <div class="explanation-card">

                    <h3>
                        🚨 Features pushing toward FRAUD
                    </h3>

                    <div class="feature-list">

                        ${
                            fraudFeatures.length === 0
                                ? `<p style="color: #6b7280; font-size: 13px; padding: 8px 0;">No significant features pushed toward fraud.</p>`
                                : fraudFeatures
                                    .slice(0, 6)
                                    .map(feature => {
                                        const val = Number(feature.shap_value) || 0;
                                        const width = Math.min((Math.abs(val) / maxShap) * 100, 100);
                                        return `
                                            <div class="shap-feature">
                                                <div class="shap-feature-header">
                                                    <strong>${feature.feature || "Feature"}</strong>
                                                    <span class="fraud-value">+${val.toFixed(3)}</span>
                                                </div>
                                                <div class="shap-bar">
                                                    <div
                                                        class="shap-bar-fraud"
                                                        style="width: ${width.toFixed(1)}%;"
                                                    ></div>
                                                </div>
                                            </div>
                                        `;
                                    })
                                    .join("")
                        }

                    </div>

                </div>


                <div class="explanation-card">

                    <h3>
                        ✅ Features pushing toward NORMAL
                    </h3>

                    <div class="feature-list">

                        ${
                            normalFeatures.length === 0
                                ? `<p style="color: #6b7280; font-size: 13px; padding: 8px 0;">No significant features pushed toward normal.</p>`
                                : normalFeatures
                                    .slice(0, 6)
                                    .map(feature => {
                                        const val = Number(feature.shap_value) || 0;
                                        const width = Math.min((Math.abs(val) / maxShap) * 100, 100);
                                        return `
                                            <div class="shap-feature">
                                                <div class="shap-feature-header">
                                                    <strong>${feature.feature || "Feature"}</strong>
                                                    <span class="normal-value">${val.toFixed(3)}</span>
                                                </div>
                                                <div class="shap-bar">
                                                    <div
                                                        class="shap-bar-normal"
                                                        style="width: ${width.toFixed(1)}%;"
                                                    ></div>
                                                </div>
                                            </div>
                                        `;
                                    })
                                    .join("")
                        }

                    </div>

                </div>

            </div>

        `;


        explanationSection.scrollIntoView({
            behavior: "smooth"
        });


    } catch (error) {

        console.error(
            "SHAP explanation error:",
            error
        );

        alert(
            "Unable to load explanation: " +
            error.message
        );

    }

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
                    ],

                    backgroundColor: [
                        "#36A2EB",
                        "#FF6384"
                    ],

                    borderColor: [
                        "#ffffff",
                        "#ffffff"
                    ],

                    borderWidth: 2
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
                                context.dataset.data.reduce(
                                    (a, b) => a + b,
                                    0
                                );

                            const percentage =
                                (value / total) * 100;

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

// ================= RECENT TRANSACTIONS =================

async function loadRecentTransactions() {

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/transactions"
        );

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(
                data.error ||
                "Unable to load transactions"
            );
        }


        const transactions =
            data.transactions || [];


        // ================= SUMMARY =================

        const totalAnalyzed =
            document.getElementById(
                "totalAnalyzed"
            );

        const fraudDetected =
            document.getElementById(
                "fraudDetected"
            );

        const normalDetected =
            document.getElementById(
                "normalDetected"
            );

        const criticalDetected =
            document.getElementById(
                "criticalDetected"
            );


        const fraudCount =
            transactions.filter(
                transaction =>
                    transaction.prediction === "FRAUD"
            ).length;


        const normalCount =
            transactions.filter(
                transaction =>
                    transaction.prediction === "NORMAL"
            ).length;


        const criticalCount =
            transactions.filter(
                transaction =>
                    transaction.risk_level === "CRITICAL"
            ).length;


        totalAnalyzed.textContent =
            transactions.length;

        fraudDetected.textContent =
            fraudCount;

        normalDetected.textContent =
            normalCount;

        criticalDetected.textContent =
            criticalCount;


        // ================= TABLE =================

        const tableBody =
            document.getElementById(
                "transactionsTableBody"
            );


        if (!tableBody) {
            return;
        }


        tableBody.innerHTML = "";


        if (transactions.length === 0) {

            tableBody.innerHTML = `
                <tr>
                    <td colspan="5">
                        No transactions available.
                    </td>
                </tr>
            `;

            return;
        }


        // ================= CREATE ROWS =================

        transactions.forEach(transaction => {

            const row =
                document.createElement("tr");


            const percentage =
                transaction.fraud_probability * 100;


            const prediction =
                transaction.prediction;


            const predictionDisplay =
                prediction === "FRAUD"
                    ? "🔴 FRAUD"
                    : "🟢 NORMAL";


            row.innerHTML = `

                <td>
                    <strong>
                        #${transaction.transaction_id}
                    </strong>
                </td>


                <td>
                    ${predictionDisplay}
                </td>


                <td>
                    ${percentage.toFixed(4)}%
                </td>


                <td>
                    <span class="risk-${transaction.risk_level.toLowerCase()}">
                        ${transaction.risk_level}
                    </span>
                </td>


                <td>

                    <button
                        class="transaction-explanation-btn"
                        type="button"
                    >
                        🔍 View Explanation
                    </button>

                </td>

            `;


            // ================= EXPLANATION BUTTON =================

            const explanationButton =
                row.querySelector(
                    ".transaction-explanation-btn"
                );


            explanationButton.addEventListener(
                "click",
                function () {

                    loadExplanationForTransaction(
                        transaction.transaction_id
                    );

                }
            );


            tableBody.appendChild(row);

        });


    } catch (error) {

        console.error(
            "Recent transactions error:",
            error
        );


        const tableBody =
            document.getElementById(
                "transactionsTableBody"
            );


        if (tableBody) {

            tableBody.innerHTML = `

                <tr>

                    <td colspan="5">

                        Unable to load transactions.

                    </td>

                </tr>

            `;

        }

    }

}




// Load transactions when page opens

loadRecentTransactions();


// ================= SIDEBAR NAVIGATION =================

const navItems =
    document.querySelectorAll(".nav-item");

navItems.forEach(item => {

    item.addEventListener("click", function () {

        const targetId =
            this.dataset.target;

        const targetSection =
            document.getElementById(targetId);

        if (!targetSection) {
            console.error(
                "Section not found:",
                targetId
            );
            return;
        }

        targetSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        // Change active button
        navItems.forEach(nav => {
            nav.classList.remove("active");
        });

        this.classList.add("active");

    });

});