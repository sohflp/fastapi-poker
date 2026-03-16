function updatePositions() {
    let rows = document.querySelectorAll("#playersTable tr")

    rows.forEach((row, index) => {
        row.querySelector(".position").value = index + 1
    })
}


function addPlayerRow() {
    removeButton.disabled = false;

    let table = document.getElementById("playersTable")
    let row = document.createElement("tr")
    let players = document.getElementById("playerOptionsTemplate").innerHTML

    row.innerHTML = `
<td>
    <input name="position" class="position bg-gray-800 p-2 rounded w-16 text-center" readonly>
</td>

<td>
    <select name="player_id" class="bg-gray-600 p-2 rounded w-36 text-center" required>
        ${players}
    </select>
</td>

<td>
    <input name="rebuys" type="number" value="0" class="bg-gray-600 p-2 rounded w-20 text-center" required>
</td>

<td>
    <input name="addons" type="number" value="0" class="bg-gray-600 p-2 rounded w-20 text-center" required>
</td>

<td>
    <input name="winnings" type="number" value="0" class="bg-gray-600 p-2 rounded w-40 text-center" required>
</td>
`
    table.appendChild(row)
    updatePositions()
}


function removeLastRow() {
    let table = document.getElementById("playersTable")
    let removeButton = document.getElementById("removeButton")

    if (table.rows.length > 1) {
        table.deleteRow(table.rows.length - 1)
        updatePositions()
    }
    
    if (table.rows.length == 1) {
        removeButton.disabled = true;
    }
}

window.onload = () => {
    addPlayerRow()
    addPlayerRow()
    addPlayerRow()
    addPlayerRow()
}