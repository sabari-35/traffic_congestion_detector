async function getAdvice() {
  try {
    const trafficData = {
  approaches: [
    {
      approach_id: "N",
      vehicle_counts: {
        car: 220,
        bus: 15,
        truck: 10,
        motorcycle: 55
      },
      queue_length: 180,
      lanes: 3,
      congestion_level: "severely_congested",
      pedestrian_count: 12,
      current_green_time: 30
    },
    {
      approach_id: "S",
      vehicle_counts: {
        car: 180,
        bus: 10,
        truck: 6,
        motorcycle: 40
      },
      queue_length: 140,
      lanes: 3,
      congestion_level: "congested",
      pedestrian_count: 10,
      current_green_time: 30
    },
    {
      approach_id: "E",
      vehicle_counts: {
        car: 90,
        auto: 25,
        motorcycle: 20
      },
      queue_length: 70,
      lanes: 2,
      congestion_level: "stable",
      pedestrian_count: 6,
      current_green_time: 30
    },
    {
      approach_id: "W",
      vehicle_counts: {
        car: 15,
        motorcycle: 5
      },
      queue_length: 15,
      lanes: 1,
      congestion_level: "free",
      pedestrian_count: 2,
      current_green_time: 30
    }
  ],
  current_cycle_time: 120,
  emergency_vehicle_present: false,
  format: "json"
};

    console.log("Sending:", trafficData);

    const res = await fetch("http://127.0.0.1:8000/advise", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(trafficData)
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
    greenTimes.innerHTML +=
      `<li><b>Approach ${dir}:</b> ${timings[dir].toFixed(1)} seconds</li>`;
  }

  // 📊 Reasoning
  data.reasoning_points.forEach(r => {
    reasoning.innerHTML += `<li>${r}</li>`;
  });

  // 🚸 Safety
  data.safety_status.checks.forEach(s => {
    safety.innerHTML += `<li>${s}</li>`;
  });

  // 👮 Police Action
  data.police_action.forEach(a => {
    policeAction.innerHTML += `<li>${a}</li>`;
  });
}
