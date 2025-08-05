document.getElementById("caseForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    fetch("/fetch_case", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("error").textContent = data.error;
            document.getElementById("parties").textContent = "";
            document.getElementById("filing_date").textContent = "";
            document.getElementById("next_hearing").textContent = "";
            document.getElementById("order_link").style.display = "none";
        } else {
            document.getElementById("error").textContent = "";
            document.getElementById("parties").textContent = data.parties || "N/A";
            document.getElementById("filing_date").textContent = data.filing_date || "N/A";
            document.getElementById("next_hearing").textContent = data.next_hearing || "N/A";
            const orderLink = document.getElementById("order_link");
            if (data.order_link && data.order_link !== "N/A") {
                orderLink.href = data.order_link;
                orderLink.style.display = "inline";
            } else {
                orderLink.style.display = "none";
            }
        }
    })
    .catch(error => {
        document.getElementById("error").textContent = "An error occurred. Please try again.";
    });
});