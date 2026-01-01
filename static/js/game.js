fetch("/get_levels")
  .then(res => res.json())
  .then(levels => {
    if (levels.length === 0) {
      document.getElementById("game-area").innerText = "No levels yet!";
      return;
    }

    const level = levels[0]; // Just load first level for demo

    const grid = document.createElement("div");
    grid.id = "grid";
    grid.style.display = "grid";
    grid.style.gridTemplateColumns = "repeat(10, 30px)";
    grid.style.gridTemplateRows = "repeat(10, 30px)";
    grid.style.gap = "2px";

    level.layout.forEach(cell => {
      const div = document.createElement("div");
      div.classList.add("cell");
      if (cell === 1) div.classList.add("wall");
      grid.appendChild(div);
    });

    document.getElementById("game-area").appendChild(grid);

    // Here you can implement BFS, DFS, Greedy, A* logic!
  });
