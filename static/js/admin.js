function showUserInfo() {
    fetch("/get_users")
      .then(res => res.json())
      .then(data => {
        let html = "<h2>User Info</h2><ul>";
        data.forEach(user => {
          html += `<li>${user.name} - Games Played: ${user.games_played}</li>`;
        });
        html += "</ul>";
        document.getElementById("content-area").innerHTML = html;
      });
  }
  
  function showGameBuilder() {
    let html = `
      <h2>Build Game Level</h2>
      <div id="grid"></div>
      <button onclick="submitLevel()">Submit Level</button>
    `;
    document.getElementById("content-area").innerHTML = html;
  
    const grid = document.getElementById("grid");
    for (let i = 0; i < 100; i++) {
      const cell = document.createElement("div");
      cell.classList.add("cell");
      cell.addEventListener("click", () => {
        cell.classList.toggle("wall");
      });
      grid.appendChild(cell);
    }
  }
  
  function submitLevel() {
    const cells = document.querySelectorAll("#grid .cell");
    const layout = Array.from(cells).map(cell => cell.classList.contains("wall") ? 1 : 0);
    fetch("/save_level", {
      method: "POST",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({layout: layout})
    })
    .then(res => res.json())
    .then(data => alert("Level Saved!"));
  }
  