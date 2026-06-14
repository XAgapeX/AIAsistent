const analyzeButton = document.getElementById("analyze-btn");
const copyButton = document.getElementById("copy-btn");
const languageSelect = document.getElementById("language");
const codeInput = document.getElementById("code-input");
const inputHighlight = document.getElementById("input-highlight");

// Funkcja do aktualizacji kolorowania składni w polu wejściowym
function updateInputHighlight() {
    let code = codeInput.value;
    
    // Zabezpieczenie przed tagami HTML w kodzie (XSS / błędy renderowania)
    code = code.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    // Prism wymaga znaku nowej linii na końcu, aby poprawnie renderować ostatnią linię
    inputHighlight.innerHTML = code + (code.endsWith("\n") ? " " : "\n");
    
    // Ustawienie klasy języka
    inputHighlight.className = `language-${languageSelect.value}`;
    
    // Wywołanie Prism
    Prism.highlightElement(inputHighlight);
}

// Synchronizacja scrollowania (pionowa i pozioma)
codeInput.addEventListener("scroll", () => {
    const pre = inputHighlight.parentElement;
    pre.scrollTop = codeInput.scrollTop;
    pre.scrollLeft = codeInput.scrollLeft;
});

// Reakcja na wpisywanie
codeInput.addEventListener("input", updateInputHighlight);

// Reakcja na zmianę języka
languageSelect.addEventListener("change", updateInputHighlight);

analyzeButton.addEventListener("click", async () => {

    const code = codeInput.value;
    const language = languageSelect.value;

    if (!code.trim()) {
        alert("Wprowadź kod do analizy!");
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
        errorDiv.textContent = data.error || (data.issues && data.issues[0]) || "Błąd analizy.";
        errorDiv.style.display = "block";
        return;
    } else {
        errorDiv.style.display = "none";
    }

    document.getElementById("score").textContent = `${data.quality_score}/10`;

    const lists = {
        "issues-list": data.issues,
        "suggestions-list": data.suggestions,
        "test-scenarios-list": data.test_scenarios
    };

    for (const [id, items] of Object.entries(lists)) {
        const el = document.getElementById(id);
        el.innerHTML = "";
        (items || []).forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            el.appendChild(li);
        });
    }

    const correctedCodeElement = document.getElementById("corrected-code");
    if (data.corrected_code) {
        correctedCodeElement.className = `language-${language}`;
        correctedCodeElement.textContent = data.corrected_code;
        Prism.highlightElement(correctedCodeElement);
        copyButton.style.display = "block";
    } else {
        correctedCodeElement.textContent = "Brak poprawionej wersji";
        copyButton.style.display = "none";
    }
});

copyButton.addEventListener("click", () => {
    const text = document.getElementById("corrected-code").textContent;
    navigator.clipboard.writeText(text).then(() => {
        const old = copyButton.textContent;
        copyButton.textContent = "Skopiowano!";
        setTimeout(() => copyButton.textContent = old, 2000);
    });
});

// Biblioteka przykładów dla różnych języków
const examples = {
    "python": `# Przykład Python: System logowania
password = "1234"

def login(username, password_input):
    if username == "admin" and password_input == password:
        print("logged in")
        return True
    return False

# Testowanie
login("admin", "1234")`,

    "javascript": `// Przykład JavaScript: Walidacja formularza
const secretKey = "API_KEY_123";

function validateUser(user) {
    if (user.role == 'admin') {
        console.log("Access granted to " + user.name);
        return true;
    }
    return false;
}

const u = { name: "John", role: "user" };
validateUser(u);`,

    "typescript": `// Przykład TypeScript: Zarządzanie produktami
interface Product {
    id: number;
    name: string;
    price: any; // Code smell!
}

class Store {
    private items: Product[] = [];

    addProduct(p: Product) {
        this.items.push(p);
    }

    getTotal(): number {
        return this.items.reduce((sum, item) => sum + item.price, 0);
    }
}

const myStore = new Store();`,

    "java": `// Przykład Java: Kalkulator pensji
public class SalaryCalculator {
    private double baseSalary = 3000.0;

    public double calculateNetto(double brutto) {
        // Brak walidacji danych wejściowych
        double tax = brutto * 0.23;
        return brutto - tax;
    }

    public static void main(String[] args) {
        SalaryCalculator calc = new SalaryCalculator();
        System.out.println(calc.calculateNetto(5000));
    }
}`,

    "csharp": `// Przykład C#: Zarządzanie bazą danych
using System;

public class DatabaseManager {
    private string connectionString = "Server=myServerAddress;Database=myData;User Id=myUsername;Password=myPassword;";

    public void Connect() {
        Console.WriteLine("Connecting with: " + connectionString);
    }

    public void ExecuteQuery(string query) {
        // Podatność na SQL Injection!
        Console.WriteLine("Executing: " + query);
    }
}`
};

document.getElementById("example-btn").addEventListener("click", () => {
    const lang = languageSelect.value;
    codeInput.value = examples[lang] || "";
    updateInputHighlight();
    analyzeButton.focus();
});
