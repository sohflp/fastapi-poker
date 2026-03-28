const levelSound = new Audio("/static/sounds/level-up.wav")
const warningSound = new Audio("/static/sounds/warning.wav")

let timerInterval
let lastLevel = -1

function startTimer() {

    let paused = localStorage.getItem("timerPaused")

    if(!localStorage.getItem("timerStart")){
        localStorage.setItem("timerStart", Date.now())
    }

    if(paused === "true"){

        let pausedAt = parseInt(localStorage.getItem("pausedAt"))
        let start = parseInt(localStorage.getItem("timerStart"))

        let pauseDuration = Date.now() - pausedAt

        localStorage.setItem("timerStart", start + pauseDuration)

    }

    localStorage.setItem("timerPaused","false")

    runTimer()

}

function pauseTimer() {

    localStorage.setItem("timerPaused", "true")
    localStorage.setItem("pausedAt", Date.now())

    clearInterval(timerInterval)

}

function resetTimer() {

    localStorage.removeItem("timerStart")
    localStorage.removeItem("timerPaused")
    localStorage.removeItem("pausedAt")

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

    if(level !== lastLevel){
        levelSound.play()
        lastLevel = level
    }

    let remaining = duration - (elapsed % duration)

    console.log(remaining)

    if(remaining <= 10 && remaining % 2 == 0){
        warningSound.play()
    }

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
        addBlindRow(100, 200)
        addBlindRow(200, 400)
        addBlindRow(300, 600)
        addBlindRow(400, 800)
        addBlindRow(500, 1000)
        addBlindRow(600, 1200)
        addBlindRow(800, 1600)
        addBlindRow(1000, 2000)
        addBlindRow(1200, 2400)
        addBlindRow(1400, 2800)
        addBlindRow(1600, 3200)
        addBlindRow(2000, 4000)
        addBlindRow(2500, 5000)
        addBlindRow(3000, 6000)
        addBlindRow(4000, 8000)
        addBlindRow(5000, 10000)
        addBlindRow(6000, 12000)
        addBlindRow(8000, 16000)
        addBlindRow(10000, 20000)
        addBlindRow(15000, 30000)
        addBlindRow(20000, 40000)
        addBlindRow(30000, 60000)
        addBlindRow(40000, 80000)
        addBlindRow(50000, 100000)
        addBlindRow(60000, 120000)
        addBlindRow(80000, 160000)
        addBlindRow(100000, 200000)
    } else {

        blinds.forEach(b => addBlindRow(b.small, b.big))

    }

}

window.onload = () => {

    loadConfig()
    runTimer()

}