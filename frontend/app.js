async function getAdvice() {
  try {
    const res = await fetch("http://127.0.0.1:8000/advise_from_video", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    console.log("Response status:", res.status);

    const data = await res.json();
    console.log("Response data:", data);

    renderAdvisory(data);
  } catch (err) {
    console.error("FETCH ERROR:", err);
    alert("Failed to fetch signal advisory. Check console.");
  }
}

function renderAdvisory(data) {
  if (!data || data.status !== "success") {
    document.getElementById("advice").innerHTML =
      "❌ Invalid advisory response";
    return;
  }

  // Clear lists
  greenTimes.innerHTML = "";
  reasoning.innerHTML = "";
  safety.innerHTML = "";
  policeAction.innerHTML = "";

  // 🟢 Green times
  const timings = data.signal_timings.per_approach;
  for (const dir in timings) {
    greenTimes.innerHTML += `<li><b>Approach ${dir}:</b> ${timings[dir].toFixed(1)} seconds</li>`;
  }

  // 📊 Reasoning
  data.reasoning_points.forEach((r) => {
    reasoning.innerHTML += `<li>${r}</li>`;
  });

  // 🚸 Safety
  data.safety_status.checks.forEach((s) => {
    safety.innerHTML += `<li>${s}</li>`;
  });

  // 👮 Police Action
  data.police_action.forEach((a) => {
    policeAction.innerHTML += `<li>${a}</li>`;
  });
}
async function getAdvice() {
  try {
    console.log("🔄 Sending request to backend...");

    const startTime = Date.now();
    const res = await fetch("http://127.0.0.1:8000/advise_from_video", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const endTime = Date.now();
    console.log(`⏱️ Response time: ${endTime - startTime}ms`);
    console.log("Response status:", res.status);
    console.log("Response headers:", res.headers);

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();
    console.log("✅ Response data received:", data);

    renderAdvisory(data);
  } catch (err) {
    console.error("❌ FETCH ERROR:", err);
    console.error("Error details:", err.message);

    // Show more specific error
    if (err.message.includes("Failed to fetch")) {
      alert(
        "Cannot connect to backend server. Make sure it's running at http://127.0.0.1:8000",
      );
    } else if (err.message.includes("HTTP error")) {
      alert(`Backend server error: ${err.message}`);
    } else {
      alert(
        "Failed to fetch signal advisory. Check browser console (F12) for details.",
      );
    }
  }
}
