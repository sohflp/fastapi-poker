function updatePositions() {
    let rows = document.querySelectorAll("#playersTable tr")

    rows.forEach((row, index) => {
        row.querySelector(".position").value = index + 1
    })
}


function addPlayerRow() {
    let table = document.getElementById("playersTable")
    let row = document.createElement("tr")

    row.innerHTML = `
<td>
    <input name="position" class="position bg-gray-800 p-2 rounded w-16 text-center" readonly>
</td>

<td>
    <input name="player_name" class="bg-gray-600 p-2 rounded w-36 text-center">
</td>

<td>
    <input name="rebuys" type="number" value="0" class="bg-gray-600 p-2 rounded w-20 text-center">
</td>

<td>
    <input name="addons" type="number" value="0" class="bg-gray-600 p-2 rounded w-20 text-center">
</td>

<td>
    <input name="winnings" type="number" value="0" class="bg-gray-600 p-2 rounded w-40 text-center">
</td>
`
    table.appendChild(row)
    updatePositions()
}


function removeLastRow() {
    let table = document.getElementById("playersTable")

    if (table.rows.length > 0) {
        table.deleteRow(table.rows.length - 1)
        updatePositions()
    }
}

window.onload = () => {
    addPlayerRow()
    addPlayerRow()
    addPlayerRow()
    addPlayerRow()
}