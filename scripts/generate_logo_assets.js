const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

function crc32(buf) {
  let crc = ~0;
  for (let i = 0; i < buf.length; i += 1) {
    crc ^= buf[i];
    for (let j = 0; j < 8; j += 1) {
      crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
    }
  }
  return ~crc >>> 0;
}

function chunk(type, data) {
  const typeBuf = Buffer.from(type);
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])));
  return Buffer.concat([len, typeBuf, data, crc]);
}

function writePng(filename, width, height, pixels) {
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 6;

  const raw = Buffer.alloc((width * 4 + 1) * height);
  for (let y = 0; y < height; y += 1) {
    const rowStart = y * (width * 4 + 1);
    raw[rowStart] = 0;
    pixels.copy(raw, rowStart + 1, y * width * 4, (y + 1) * width * 4);
  }

  const png = Buffer.concat([
    signature,
    chunk("IHDR", ihdr),
    chunk("IDAT", zlib.deflateSync(raw, { level: 9 })),
    chunk("IEND", Buffer.alloc(0)),
  ]);
  fs.writeFileSync(filename, png);
}

function canvas(width, height) {
  return Buffer.alloc(width * height * 4);
}

function blend(dst, idx, color) {
  const a = color[3] / 255;
  const inv = 1 - a;
  dst[idx] = Math.round(color[0] * a + dst[idx] * inv);
  dst[idx + 1] = Math.round(color[1] * a + dst[idx + 1] * inv);
  dst[idx + 2] = Math.round(color[2] * a + dst[idx + 2] * inv);
  dst[idx + 3] = Math.round(255 * (a + (dst[idx + 3] / 255) * inv));
}

function mix(a, b, t) {
  return [
    Math.round(a[0] + (b[0] - a[0]) * t),
    Math.round(a[1] + (b[1] - a[1]) * t),
    Math.round(a[2] + (b[2] - a[2]) * t),
    Math.round(a[3] + (b[3] - a[3]) * t),
  ];
}

function rect(pixels, w, h, x, y, rw, rh, color) {
  const x0 = Math.max(0, Math.floor(x));
  const y0 = Math.max(0, Math.floor(y));
  const x1 = Math.min(w, Math.ceil(x + rw));
  const y1 = Math.min(h, Math.ceil(y + rh));
  for (let py = y0; py < y1; py += 1) {
    for (let px = x0; px < x1; px += 1) {
      blend(pixels, (py * w + px) * 4, color);
    }
  }
}

function roundedRect(pixels, w, h, x, y, rw, rh, r, colorA, colorB) {
  const x0 = Math.max(0, Math.floor(x));
  const y0 = Math.max(0, Math.floor(y));
  const x1 = Math.min(w, Math.ceil(x + rw));
  const y1 = Math.min(h, Math.ceil(y + rh));
  for (let py = y0; py < y1; py += 1) {
    for (let px = x0; px < x1; px += 1) {
      const qx = Math.max(x + r - px, 0, px - (x + rw - r));
      const qy = Math.max(y + r - py, 0, py - (y + rh - r));
      const dist = Math.sqrt(qx * qx + qy * qy);
      if (dist <= r) {
        const edgeAlpha = Math.max(0, Math.min(1, r - dist));
        const t = (px - x + py - y) / (rw + rh);
        const color = mix(colorA, colorB, Math.max(0, Math.min(1, t)));
        color[3] = Math.round(color[3] * Math.min(1, edgeAlpha + 0.4));
        blend(pixels, (py * w + px) * 4, color);
      }
    }
  }
}

function circle(pixels, w, h, cx, cy, radius, colorA, colorB) {
  const x0 = Math.max(0, Math.floor(cx - radius));
  const y0 = Math.max(0, Math.floor(cy - radius));
  const x1 = Math.min(w, Math.ceil(cx + radius));
  const y1 = Math.min(h, Math.ceil(cy + radius));
  for (let py = y0; py < y1; py += 1) {
    for (let px = x0; px < x1; px += 1) {
      const dx = px - cx;
      const dy = py - cy;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d <= radius) {
        const t = Math.max(0, Math.min(1, (dx + dy + radius * 2) / (radius * 4)));
        const color = mix(colorA, colorB, t);
        color[3] = Math.round(color[3] * Math.min(1, radius - d + 0.6));
        blend(pixels, (py * w + px) * 4, color);
      }
    }
  }
}

function thickLine(pixels, w, h, x1, y1, x2, y2, thickness, color) {
  const minX = Math.max(0, Math.floor(Math.min(x1, x2) - thickness));
  const maxX = Math.min(w, Math.ceil(Math.max(x1, x2) + thickness));
  const minY = Math.max(0, Math.floor(Math.min(y1, y2) - thickness));
  const maxY = Math.min(h, Math.ceil(Math.max(y1, y2) + thickness));
  const vx = x2 - x1;
  const vy = y2 - y1;
  const len2 = vx * vx + vy * vy;
  for (let y = minY; y < maxY; y += 1) {
    for (let x = minX; x < maxX; x += 1) {
      const t = Math.max(0, Math.min(1, ((x - x1) * vx + (y - y1) * vy) / len2));
      const px = x1 + t * vx;
      const py = y1 + t * vy;
      const d = Math.hypot(x - px, y - py);
      if (d <= thickness / 2) {
        const edge = Math.max(0, Math.min(1, thickness / 2 - d + 0.75));
        blend(pixels, (y * w + x) * 4, [color[0], color[1], color[2], Math.round(color[3] * edge)]);
      }
    }
  }
}

function polygon(pixels, w, h, points, color) {
  const minX = Math.max(0, Math.floor(Math.min(...points.map((p) => p[0]))));
  const maxX = Math.min(w, Math.ceil(Math.max(...points.map((p) => p[0]))));
  const minY = Math.max(0, Math.floor(Math.min(...points.map((p) => p[1]))));
  const maxY = Math.min(h, Math.ceil(Math.max(...points.map((p) => p[1]))));
  for (let y = minY; y < maxY; y += 1) {
    for (let x = minX; x < maxX; x += 1) {
      let inside = false;
      for (let i = 0, j = points.length - 1; i < points.length; j = i, i += 1) {
        const xi = points[i][0];
        const yi = points[i][1];
        const xj = points[j][0];
        const yj = points[j][1];
        const intersect = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
        if (intersect) inside = !inside;
      }
      if (inside) blend(pixels, (y * w + x) * 4, color);
    }
  }
}

function drawMark(size) {
  const pixels = canvas(size, size);
  const s = size / 1024;

  circle(pixels, size, size, 512 * s, 512 * s, 424 * s, [15, 35, 64, 255], [22, 86, 118, 255]);
  circle(pixels, size, size, 362 * s, 278 * s, 150 * s, [74, 222, 128, 36], [56, 189, 248, 22]);
  roundedRect(pixels, size, size, 214 * s, 206 * s, 596 * s, 596 * s, 118 * s, [10, 22, 44, 235], [16, 72, 96, 238]);
  roundedRect(pixels, size, size, 252 * s, 244 * s, 520 * s, 520 * s, 86 * s, [19, 44, 73, 210], [13, 148, 136, 90]);

  const bars = [
    [330, 598, 86, 144, [45, 212, 191, 255], [96, 165, 250, 255]],
    [452, 518, 86, 224, [56, 189, 248, 255], [99, 102, 241, 255]],
    [574, 424, 86, 318, [132, 204, 22, 255], [34, 197, 94, 255]],
  ];
  bars.forEach(([x, y, bw, bh, a, b]) => {
    roundedRect(pixels, size, size, x * s, y * s, bw * s, bh * s, 28 * s, a, b);
  });

  thickLine(pixels, size, size, 316 * s, 484 * s, 442 * s, 426 * s, 34 * s, [245, 158, 11, 255]);
  thickLine(pixels, size, size, 442 * s, 426 * s, 548 * s, 320 * s, 34 * s, [245, 158, 11, 255]);
  thickLine(pixels, size, size, 548 * s, 320 * s, 690 * s, 260 * s, 34 * s, [245, 158, 11, 255]);
  polygon(
    pixels,
    size,
    size,
    [
      [692 * s, 222 * s],
      [754 * s, 276 * s],
      [676 * s, 306 * s],
    ],
    [245, 158, 11, 255],
  );

  circle(pixels, size, size, 316 * s, 484 * s, 24 * s, [255, 255, 255, 255], [209, 250, 229, 255]);
  circle(pixels, size, size, 548 * s, 320 * s, 24 * s, [255, 255, 255, 255], [209, 250, 229, 255]);
  circle(pixels, size, size, 690 * s, 260 * s, 24 * s, [255, 255, 255, 255], [209, 250, 229, 255]);

  return pixels;
}

const assetsDir = path.join(__dirname, "..", "assets");
fs.mkdirSync(assetsDir, { recursive: true });
writePng(path.join(assetsDir, "logo.png"), 1024, 1024, drawMark(1024));
writePng(path.join(assetsDir, "company_icon.png"), 512, 512, drawMark(512));
console.log("Generated assets/logo.png and assets/company_icon.png");
