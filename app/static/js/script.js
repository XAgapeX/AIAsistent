const analyzeButton = document.getElementById("analyze-btn");
const copyButton = document.getElementById("copy-btn");

analyzeButton.addEventListener("click", async () => {

    const code = document.getElementById("code-input").value;
    const language = document.getElementById("language").value;

    if (!code.trim()) {
        alert("Please enter some code to analyze!");
        return;
    }

    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analizuję...";

    const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            code: code,
            language: language
        })
    });

    analyzeButton.disabled = false;
    analyzeButton.textContent = "Analizuj Kod i Generuj Testy";

    const data = await response.json();

    const errorDiv = document.getElementById("error-message");

    if (data.error || data.quality_score === 0) {
        errorDiv.textContent = data.error || data.issues[0];
        errorDiv.style.display = "block";
        return;
    } else {
        errorDiv.style.display = "none";
    }

    document.getElementById("score").textContent =
        `${data.quality_score}/10`;

    const issuesList = document.getElementById("issues-list");
    issuesList.innerHTML = "";

    data.issues.forEach(issue => {
        const li = document.createElement("li");
        li.textContent = issue;
        issuesList.appendChild(li);
    });

    const suggestionsList = document.getElementById("suggestions-list");
    suggestionsList.innerHTML = "";

    data.suggestions.forEach(suggestion => {
        const li = document.createElement("li");
        li.textContent = suggestion;
        suggestionsList.appendChild(li);
    });

    const scenariosList = document.getElementById("test-scenarios-list");
    scenariosList.innerHTML = "";

    if (data.test_scenarios && data.test_scenarios.length > 0) {
        data.test_scenarios.forEach(scenario => {
            const li = document.createElement("li");
            li.textContent = scenario;
            scenariosList.appendChild(li);
        });
    } else {
        scenariosList.innerHTML = "<li>Brak scenariuszy testowych</li>";
    }

    // Wyświetlanie poprawionego kodu
    const correctedCodeElement = document.getElementById("corrected-code");
    if (data.corrected_code) {
        correctedCodeElement.textContent = data.corrected_code;
        copyButton.style.display = "block";
    } else {
        correctedCodeElement.textContent = "Brak poprawionej wersji";
        copyButton.style.display = "none";
    }

});

// Przycisk Copy to Clipboard
copyButton.addEventListener("click", () => {
    const correctedCode = document.getElementById("corrected-code").textContent;
    navigator.clipboard.writeText(correctedCode).then(() => {
        const originalText = copyButton.textContent;
        copyButton.textContent = "Skopiowano!";
        setTimeout(() => {
            copyButton.textContent = originalText;
        }, 2000);
    }).catch(err => {
        alert("Błąd kopiowania");
    });
});

// Przycisk Load Example Code
const exampleButton = document.getElementById("example-btn");
exampleButton.addEventListener("click", () => {
    const exampleCode = `# Przykład: System logowania użytkowników

password = "1234"

def login(username, password_input):
    if username == "admin" and password_input == password:
        print("logged in")
        return True
    return False

# Testowanie
users = ["John", "Kate", "Mike"]
for i in range(len(users)):
    print(users[i])

# Zalogowanie
login("admin", "1234")`;

    document.getElementById("code-input").value = exampleCode;
    document.getElementById("language").value = "python";
    analyzeButton.focus();
});
