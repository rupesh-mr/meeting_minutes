document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const progress = document.getElementById("progress");
  const progressBar = document.getElementById("progress-bar");
  const historyList = document.getElementById("history-list");

  function fetchHistory() {
    axios.get("/history")
      .then(res => {
        historyList.innerHTML = "";
        res.data.forEach(item => {
          const div = document.createElement("div");
          div.className = "meeting";
          div.innerHTML = `<strong>${item.datetime}</strong><br>${item.summary}`;
          historyList.appendChild(div);

          if (item.dates && item.dates.length > 0) {
            showEventSuggestions(item.summary, item.dates);
          }
        });
      })
      .catch(err => {
        historyList.innerHTML = "⚠️ Failed to load history.";
      });
  }

  function showEventSuggestions(summary, dates) {
    const calendarDiv = document.createElement("div");
    calendarDiv.className = "calendar-suggestions";

    dates.forEach(date => {
      const btn = document.createElement("button");
      btn.className = "calendar-btn";
      btn.textContent = `📅 Add \"${summary}\" on ${date}`;
      btn.onclick = () => {
        axios.post("/add_event", { summary, date })
          .then(() => alert(`✅ Event added for ${date}`))
          .catch(() => alert("⚠️ Failed to add event."));
      };
      calendarDiv.appendChild(btn);
    });

    historyList.prepend(calendarDiv);
  }

  fetchHistory();

  let progressInterval;
  function simulateProgress(durationSec) {
    let elapsed = 0;
    progress.style.display = "block";
    progressBar.style.width = "0%";
    progressBar.textContent = "0%";

    progressInterval = setInterval(() => {
      elapsed++;
      const percent = Math.min((elapsed / durationSec) * 100, 100);
      progressBar.style.width = `${percent.toFixed(0)}%`;
      progressBar.textContent = `${percent.toFixed(0)}%`;

      if (percent >= 100) clearInterval(progressInterval);
    }, 1000);
  }

  startBtn.addEventListener("click", () => {
    startBtn.disabled = true;
    stopBtn.disabled = false;
    axios.post("/start")
      .then(() => console.log("🎙 Recording started"))
      .catch(() => alert("⚠️ Failed to start recording."));
  });

  stopBtn.addEventListener("click", () => {
    stopBtn.disabled = true;
    simulateProgress(30); // show 30s progress bar

    axios.post("/stop")
      .then(() => {
        console.log("⏹ Recording stopped");
        // Poll /status for completion
        const poll = setInterval(() => {
          axios.get("/status").then(res => {
            if (res.data.status === "idle") {
              clearInterval(poll);
              fetchHistory();
              progress.style.display = "none";
              startBtn.disabled = false;
            }
          });
        }, 2000);
      })
      .catch(() => alert("⚠️ Failed to stop recording."));
  });
});
