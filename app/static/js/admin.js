function addPlayerRow() {
    let table = document.getElementById("playersTable")
    let row = table.insertRow()

    row.innerHTML = `
<td>
<input name="position" type="number" class="bg-gray-600 p-3 rounded w-20">
</td>
<td>
<input name="player_name" class="bg-gray-600 p-3 w-100 rounded">
</td>
<td>
<input name="rebuys" type="number" value="0" class="bg-gray-600 p-3 rounded w-20">
</td>
<td>
<input name="addons" type="checkbox" class="bg-gray-600 p-3 rounded w-20">
</td>
`
}