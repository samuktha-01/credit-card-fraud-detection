const normalBtn = document.getElementById("normalBtn");
const fraudBtn = document.getElementById("fraudBtn");

const resultBox = document.getElementById("result");
const predictionText = document.getElementById("prediction");
const probabilityText = document.getElementById("probability");


async function testTransaction(type) {

    resultBox.classList.remove("hidden");
    resultBox.className = "result loading";

    predictionText.textContent = "Checking transaction...";
    probabilityText.textContent = "Please wait";

    normalBtn.disabled = true;
    fraudBtn.disabled = true;

    try {

        const response = await fetch(
            `http://127.0.0.1:8000/demo/${type}`
        );

        if (!response.ok) {
            throw new Error("API request failed");
        }

        const data = await response.json();

        const percentage = data.fraud_probability * 100;

        if (data.prediction === "FRAUD") {

            resultBox.className = "result fraud";

            predictionText.textContent =
                "🚨 FRAUD DETECTED";

        } else {

            resultBox.className = "result normal";

            predictionText.textContent =
                "✅ TRANSACTION IS NORMAL";
        }

        probabilityText.textContent =
            percentage.toFixed(4) + "%";

    } catch (error) {

        console.error(error);

        resultBox.className = "result error";

        predictionText.textContent =
            "❌ API ERROR";

        probabilityText.textContent =
            "Could not connect to API";
    }

    normalBtn.disabled = false;
    fraudBtn.disabled = false;
}


normalBtn.addEventListener("click", function () {
    testTransaction("normal");
});


fraudBtn.addEventListener("click", function () {
    testTransaction("fraud");
});