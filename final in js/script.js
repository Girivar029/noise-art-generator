const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

const WIDTH = 800, HEIGHT = 550, BLOCK_SIZE = 8;
const LOW_W = Math.floor(WIDTH / BLOCK_SIZE), LOW_H = Math.floor(HEIGHT / BLOCK_SIZE);

const palettes = {
  red: [
    [32,5,8],[60,10,14],[90,18,22],[120,24,27],
    [150,34,35],[180,44,46],[210,58,63]
  ],
  purple: [
    [18,5,30],[32,10,50],[50,18,75],[64,24,95],
    [85,35,120],[110,50,150],[140,65,190]
  ],
  blue: [
    [7,13,23],[14,23,38],[22,32,54],[33,47,80],
    [46,69,104],[60,90,138],[80,120,178]
  ],
  dark_brown: [
    [14,9,6],[19,13,9],[29,20,13],[38,26,16],
    [48,33,22],[59,40,28],[80,55,40]
  ]
};

function lerpColor(a, b, t) {
  return [
    Math.round(a[0] * (1-t) + b[0] * t),
    Math.round(a[1] * (1-t) + b[1] * t),
    Math.round(a[2] * (1-t) + b[2] * t)
  ];
}

function setPixel(ix, iy, color) {
  ctx.fillStyle = `rgb(${color[0]},${color[1]},${color[2]})`;
  ctx.fillRect(ix*BLOCK_SIZE, iy*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
}

function drawGradientBG(palette) {
  for (let y = 0; y < LOW_H; y++) {
    let t = y / (LOW_H - 1);
    let idxFloat = t * (palette.length - 1);
    let idx = Math.floor(idxFloat);
    let frac = idxFloat - idx;
    let col = lerpColor(palette[idx], palette[Math.min(idx+1, palette.length-1)], frac);
    for (let x = 0; x < LOW_W; x++) setPixel(x, y, col);
  }
}

function drawPlanet(cx, cy, r, palette) {
  const bands = palette.length;
  for (let y = -r; y <= r; y++) {
    for (let x = -r; x <= r; x++) {
      if (x * x + y * y <= r * r) {
        const rx = cx + x;
        const ry = cy + y;
        if (rx >= 0 && rx < LOW_W && ry >= 0 && ry < LOW_H) {
          const norm = Math.sqrt(x * x + y * y) / r;
          let idx = Math.floor(norm * (bands - 1));
          idx = Math.min(Math.max(idx,0), bands-1);
          let col = palette[idx];
          setPixel(rx, ry, col);
          if (Math.abs(norm - 1) < 0.08) {
            let highlight = lerpColor(col, [255, 255, 255], 0.8);
            setPixel(rx, ry, highlight);
          }
        }
      }
    }
  }
}

function drawRings(cx, cy, r, palette, rings = 3, fade = 15) {
  for (let ring = 1; ring <= rings; ring++) {
    const ringRadius = r + ring * 10;
    const alpha = 1 - ring / (rings + 1);
    const colBase = palette[palette.length - 1];
    const ringCol = colBase.map(c => Math.floor(c * alpha));

    for (let theta = 0; theta < 360; theta += 4) {
      const rad = (theta * Math.PI) / 180;
      const x = Math.floor(cx + ringRadius * Math.cos(rad));
      const y = Math.floor(cy + ringRadius * Math.sin(rad));
      if (x >= 0 && x < LOW_W && y >= 0 && y < LOW_H) {
        setPixel(x, y, ringCol);
      }
    }
  }
}

function randomSafePlanetPositions(n, min_r, max_r) {
  let poses = [];
  let attempts = 0;
  while (poses.length < n && attempts < n * 20) {
    let r = Math.floor(Math.random() * (max_r - min_r + 1)) + min_r;
    let cx = Math.floor(Math.random() * (LOW_W - 2 * r - 32)) + r + 16;
    let cy = Math.floor(Math.random() * (LOW_H - 2 * r - 32)) + r + 16;
    if (poses.every(([x, y, rr]) => Math.hypot(cx - x, cy - y) > rr + r + 28)) {
      poses.push([cx, cy, r]);
    }
    attempts++;
  }
  return poses;
}

function generatePlanets(n, paletteType) {
  const basePalette = palettes[paletteType];
  const planetPalette = basePalette;

  const positions = randomSafePlanetPositions(n, 10, 20);
  positions.forEach(([cx, cy, r]) => {
    drawPlanet(cx, cy, r, planetPalette);
    let rings = Math.floor(Math.random() * 3) + 1;
    drawRings(cx, cy, r, planetPalette, rings);
  });
}

function main() {
  drawGradientBG(palettes.blue);
  generatePlanets(3, "blue");
}

main();

window.addEventListener('keydown', (e) => {
  if (e.key === " ") {
    ctx.clearRect(0, 0, WIDTH, HEIGHT);
    main();
  }
  if (e.key.toLowerCase() === "s") {
    const link = document.createElement('a');
    link.download = 'space_art.png';
    link.href = canvas.toDataURL();
    link.click();
  }
});
