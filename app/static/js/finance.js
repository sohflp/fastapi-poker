let sortDirection = {};
let lastSortedColumn = null;

function sortTable(columnIndex) {

    const table = document.querySelector("table tbody");
    const rows = Array.from(table.querySelectorAll("tr"));

    // Toggle direction
    sortDirection[columnIndex] = !sortDirection[columnIndex];
    const asc = sortDirection[columnIndex];

    // Sort rows
    rows.sort((a, b) => {

        let A = a.children[columnIndex].innerText.trim();
        let B = b.children[columnIndex].innerText.trim();

        // Clean emojis/symbols
        A = A.replace(/[^a-zA-Z0-9.-]/g, "");
        B = B.replace(/[^a-zA-Z0-9.-]/g, "");

        let numA = parseFloat(A);
        let numB = parseFloat(B);

        if (!isNaN(numA) && !isNaN(numB)) {
            return asc ? numA - numB : numB - numA;
        }

        return asc ? A.localeCompare(B) : B.localeCompare(A);
    });

    rows.forEach(row => table.appendChild(row));

    updateSortIndicators(columnIndex, asc);
}

function updateSortIndicators(columnIndex, asc) {

    const headers = document.querySelectorAll("th");

    // Clear all indicators
    headers.forEach(th => {
        th.innerText = th.innerText.replace(/ ▲| ▼/g, "");
    });

    // Add indicator to active column
    const activeHeader = document.querySelector(`th[data-col="${columnIndex}"]`);

    if (activeHeader) {
        activeHeader.innerText += asc ? " ▲" : " ▼";
    }

    lastSortedColumn = columnIndex;
}