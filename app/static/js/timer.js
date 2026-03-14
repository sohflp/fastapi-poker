let timerInterval

function startTimer() {

    if (!localStorage.getItem("timerStart")) {
        localStorage.setItem("timerStart", Date.now())
    }

    localStorage.setItem("timerPaused", "false")

    runTimer()

}

function pauseTimer() {

    localStorage.setItem("timerPaused", "true")

    clearInterval(timerInterval)

}

function resetTimer() {

    localStorage.removeItem("timerStart")

    clearInterval(timerInterval)

    document.getElementById("timer").innerText = "00:00"

}

function runTimer() {

    timerInterval = setInterval(updateTimer, 1000)

}

function getBlinds() {

    let rows = document.querySelectorAll("#blindTable tr")

    let blinds = []

    rows.forEach(row => {

        let small = row.querySelector(".small").value
        let big = row.querySelector(".big").value

        blinds.push({
            small: parseInt(small),
            big: parseInt(big)
        })

    })

    return blinds

}

function updateTimer() {

    if (localStorage.getItem("timerPaused") === "true") return

    let start = localStorage.getItem("timerStart")
    if (!start) return

    let duration = parseInt(localStorage.getItem("levelDuration") || 600)

    let blinds = JSON.parse(localStorage.getItem("blinds") || "[]")

    let elapsed = Math.floor((Date.now() - start) / 1000)

    let level = Math.floor(elapsed / duration)

    let remaining = duration - (elapsed % duration)

    let minutes = Math.floor(remaining / 60)
    let seconds = remaining % 60

    document.getElementById("timer").innerText =
        minutes + ":" + String(seconds).padStart(2, '0')

    document.getElementById("level").innerText = level + 1

    if (blinds[level]) {

        document.getElementById("blinds").innerText =
            blinds[level].small + " / " + blinds[level].big

    }

}

function addBlindRow(small = "", big = "") {

    let table = document.getElementById("blindTable")

    let row = document.createElement("tr")

    row.innerHTML = `
<td><input type="number" class="small bg-gray-600 p-2 rounded w-24" value="${small}"></td>
<td><input type="number" class="big bg-gray-600 p-2 rounded w-24" value="${big}"></td>
<td><button onclick="this.parentElement.parentElement.remove()" class="text-red-400">Remove</button></td>
`

    table.appendChild(row)

}

function saveConfig() {

    let minutes = document.getElementById("duration").value

    let seconds = minutes * 60

    localStorage.setItem("levelDuration", seconds)

    let blinds = getBlinds()

    localStorage.setItem("blinds", JSON.stringify(blinds))

    alert("Configuration saved")

}

function loadConfig() {

    let duration = localStorage.getItem("levelDuration")

    if (duration) {

        document.getElementById("duration").value = duration / 60

    }

    let blinds = JSON.parse(localStorage.getItem("blinds") || "[]")

    if (blinds.length === 0) {

        addBlindRow(25, 50)
        addBlindRow(50, 100)
        addBlindRow(100, 200)

    } else {

        blinds.forEach(b => addBlindRow(b.small, b.big))

    }

}

window.onload = () => {

    loadConfig()
    runTimer()

}