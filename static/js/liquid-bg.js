/**
 * RoadRescue — Liquid Glass Background Engine v2
 * Vivid, colorful blobs that create a stunning canvas behind the glass UI.
 * Reacts to: mouse movement (repulsion), clicks (burst + ripple), scroll (parallax).
 */
(function () {
  'use strict';

  const CFG = {
    blobCount: 6,
    speed: 0.00055,
    morphSpeed: 0.0009,
    morphAmount: 0.38,
    mouseInfluence: 220,
    mouseForce: 0.07,
    clickBurst: 100,
    scrollTilt: 0.5,
    opacity: 0.72,
    blur: 70,
    palette: [
      [99,  102, 241],   // indigo
      [59,  130, 246],   // blue
      [16,  185, 129],   // emerald
      [245, 101,  101],  // rose (emergency accent)
      [139,  92, 246],   // violet
      [6,   182, 212],   // cyan
    ],
  };

  const canvas = document.createElement('canvas');
  canvas.id = 'liquid-canvas';
  Object.assign(canvas.style, {
    position: 'fixed', inset: '0', zIndex: '-1',
    pointerEvents: 'none', width: '100%', height: '100%',
  });
  document.body.prepend(canvas);
  const ctx = canvas.getContext('2d');

  let W = 0, H = 0;
  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  resize();
  window.addEventListener('resize', () => { resize(); initBlobs(); });

  let mouse = { x: W / 2, y: H / 2 };
  let scrollY = 0;
  let ripples = [];

  window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
  window.addEventListener('scroll', () => { scrollY = window.scrollY; });
  window.addEventListener('click', e => {
    ripples.push({ x: e.clientX, y: e.clientY, r: 0, maxR: 500, alpha: 0.6 });
    blobs.forEach(b => {
      const dx = b.x - e.clientX, dy = b.y - e.clientY;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      if (dist < CFG.baseRadius * 2.5) {
        const force = CFG.clickBurst / dist;
        b.vx += (dx / dist) * force;
        b.vy += (dy / dist) * force;
      }
    });
  });

  class Blob {
    constructor(i) {
      this.i = i;
      this.r = (Math.min(W, H) * 0.28) * (0.65 + Math.random() * 0.7);
      this.color = CFG.palette[i % CFG.palette.length];
      this.angle = (i / CFG.blobCount) * Math.PI * 2 + Math.random() * 0.5;
      this.orbitScale = 0.2 + Math.random() * 0.18;
      this.x = W / 2 + Math.cos(this.angle) * Math.min(W, H) * this.orbitScale;
      this.y = H / 2 + Math.sin(this.angle) * Math.min(W, H) * this.orbitScale;
      this.vx = 0; this.vy = 0;
      this.phase = Math.random() * Math.PI * 2;
      this.mPhase = Math.random() * Math.PI * 2;
      this.spd = 0.5 + Math.random() * 1.1;
    }

    update(t) {
      this.angle += CFG.speed * this.spd;
      const orbitR = Math.min(W, H) * (this.orbitScale + Math.sin(t * 0.0002 + this.phase) * 0.05);
      const tx = W / 2 + Math.cos(this.angle) * orbitR;
      const ty = H / 2 + Math.sin(this.angle) * orbitR
               - scrollY * CFG.scrollTilt * ((this.i % 3) - 1) * 0.12;

      const dx = this.x - mouse.x, dy = this.y - mouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      if (dist < CFG.mouseInfluence) {
        const f = ((CFG.mouseInfluence - dist) / CFG.mouseInfluence) * CFG.mouseForce;
        this.vx += (dx / dist) * f * (this.r * 0.4);
        this.vy += (dy / dist) * f * (this.r * 0.4);
      }

      this.vx += (tx - this.x) * 0.014;
      this.vy += (ty - this.y) * 0.014;
      this.vx *= 0.87; this.vy *= 0.87;
      this.x += this.vx; this.y += this.vy;
      this.mPhase += CFG.morphSpeed * this.spd;
    }

    draw(t) {
      const [r, g, b] = this.color;
      const pts = 10;
      ctx.beginPath();
      for (let i = 0; i <= pts; i++) {
        const a = (i / pts) * Math.PI * 2;
        const wobble =
          Math.sin(a * 2 + this.mPhase) * CFG.morphAmount * this.r * 0.4 +
          Math.sin(a * 3 + this.mPhase * 0.8) * CFG.morphAmount * this.r * 0.22 +
          Math.sin(a * 6 + t * 0.0006) * CFG.morphAmount * this.r * 0.1;
        const rad = this.r + wobble;
        const px = this.x + Math.cos(a) * rad, py = this.y + Math.sin(a) * rad;
        if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
      }
      ctx.closePath();

      const grd = ctx.createRadialGradient(this.x - this.r * 0.2, this.y - this.r * 0.2, 0, this.x, this.y, this.r * 1.2);
      grd.addColorStop(0,   `rgba(${r},${g},${b},${CFG.opacity})`);
      grd.addColorStop(0.55,`rgba(${r},${g},${b},${CFG.opacity * 0.75})`);
      grd.addColorStop(1,   `rgba(${r},${g},${b},0)`);
      ctx.fillStyle = grd;
      ctx.fill();
    }
  }

  let blobs = [];
  function initBlobs() { blobs = Array.from({ length: CFG.blobCount }, (_, i) => new Blob(i)); }
  initBlobs();

  function drawRipples() {
    ripples = ripples.filter(rp => rp.r < rp.maxR);
    ripples.forEach(rp => {
      rp.r += 7;
      rp.alpha = Math.max(0, 0.5 * (1 - rp.r / rp.maxR));
      ctx.beginPath();
      ctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(255,255,255,${rp.alpha})`;
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  }

  function loop(t) {
    ctx.clearRect(0, 0, W, H);
    ctx.save();
    ctx.filter = `blur(${CFG.blur}px)`;
    blobs.forEach(b => { b.update(t); b.draw(t); });
    ctx.restore();
    drawRipples();
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

})();
