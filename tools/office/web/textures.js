// Canvas textures shared by the floor and its surroundings.
import * as THREE from "three";

export const FONT_STACK = '"Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif';

export function mulberry32(seed) {
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function glyphPixels(ch) {
  const c = document.createElement("canvas");
  c.width = c.height = 48;
  const g = c.getContext("2d");
  g.font = `40px ${FONT_STACK}`;
  g.textBaseline = "top";
  g.fillText(ch, 2, 2);
  return c.toDataURL();
}

// No Hangul font at all: the glyph then equals the "missing" box, so signs fall back to Latin.
export const hangulAvailable = () => glyphPixels("제") !== glyphPixels("\u{10FFFF}");

// A sign with a label; `sub` is a smaller line under it (the name in Latin letters, for those who do not read Hangul).
export function signTexture(label, color, sub = null) {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 160;
  const g = c.getContext("2d");
  g.fillStyle = "rgba(8, 10, 24, 0.82)";
  g.beginPath();
  g.roundRect(8, 8, 496, 144, 24);
  g.fill();
  g.font = `bold ${sub ? 78 : label.length > 4 ? 64 : 96}px ${FONT_STACK}`;
  g.textAlign = "center";
  g.textBaseline = "middle";
  g.fillStyle = color;
  g.shadowColor = color;
  const y = sub ? 66 : 84;
  g.shadowBlur = 28;
  g.fillText(label, 256, y);
  g.shadowBlur = 8;
  g.fillText(label, 256, y);
  if (sub) {
    g.shadowBlur = 0;
    g.font = `700 30px ${FONT_STACK}`;
    g.letterSpacing = "8px";
    g.fillStyle = "#e6e9f5";
    g.fillText(sub, 256, 122);
    g.letterSpacing = "0px";
    g.shadowColor = color;
  }
  g.strokeStyle = color;
  g.lineWidth = 5;
  g.shadowBlur = 16;
  g.beginPath();
  g.roundRect(8, 8, 496, 144, 24);
  g.stroke();
  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}
