// Page-side helpers driven by render.py. All motion is done with CSS
// transitions/animations or element.animate() so render.py can pause and
// seek every animation frame-by-frame through the Web Animations API.
(() => {
  const stage = () => document.getElementById('stage');
  let fresh = [];

  window.setScene = (html) => {
    for (const old of stage().querySelectorAll('.scene')) {
      if (old.classList.contains('leave')) old.remove();
      else {
        for (const a of old.getAnimations()) a.cancel();
        old.classList.add('leave');
      }
    }
    const el = document.createElement('div');
    el.className = 'scene entering';
    el.innerHTML = html;
    stage().appendChild(el);
    for (const r of document.querySelectorAll('.ripple')) r.remove();
    hideCursor();
  };

  window.dropLeaving = () => {
    for (const old of stage().querySelectorAll('.scene.leave')) old.remove();
    for (const s of stage().querySelectorAll('.scene.entering')) s.classList.remove('entering');
  };

  const cur = () => document.querySelector('.scene:not(.leave)');

  // Layout box relative to the page, ignoring in-flight transforms (scene
  // entrance, reveal offsets) so pointers land where the element settles.
  const box = (sel) => {
    const el = cur().querySelector(sel);
    let x = 0, y = 0;
    for (let e = el; e && e !== document.body; e = e.offsetParent) { x += e.offsetLeft; y += e.offsetTop; }
    return { left: x, top: y, width: el.offsetWidth, height: el.offsetHeight };
  };

  window.reveal = (k) => {
    for (const el of cur().querySelectorAll(`[data-s="${k}"]`)) el.classList.add('on');
    for (const el of cur().querySelectorAll(`[data-hide="${k}"]`)) el.classList.add('off');
  };

  window.setSub = (t) => { document.getElementById('sub').textContent = t; };

  // Fake mouse pointer: glides to the centre of `sel`, optionally clicks.
  let cx = 1700, cy = 900;
  function hideCursor() { document.getElementById('cursor').style.opacity = 0; }
  window.cursor = (sel, opts = {}) => {
    const c = document.getElementById('cursor');
    const r = box(sel);
    const x = r.left + r.width * (opts.fx ?? 0.5), y = r.top + r.height * (opts.fy ?? 0.5);
    const delay = opts.delay ?? 300, dur = opts.dur ?? 800;
    c.style.opacity = 1;
    c.animate([{ transform: `translate(${cx}px,${cy}px)` }, { transform: `translate(${x}px,${y}px)` }],
      { duration: dur, delay, easing: 'cubic-bezier(.45,0,.2,1)', fill: 'both' });
    cx = x; cy = y;
    if (opts.click) {
      const rp = document.createElement('div');
      rp.className = 'ripple';
      rp.style.left = x + 'px'; rp.style.top = y + 'px';
      document.body.appendChild(rp);
      rp.animate([{ transform: 'translate(-50%,-50%) scale(.2)', opacity: .9 },
                  { transform: 'translate(-50%,-50%) scale(1.6)', opacity: 0 }],
        { duration: 600, delay: delay + dur, fill: 'both' });
    }
  };

  // Rounded highlight ring around an element in the current scene.
  window.hl = (sel, opts = {}) => {
    for (const h of document.querySelectorAll('.hl')) h.remove();
    if (!sel) return;
    const r = box(sel);
    const p = opts.pad ?? 10;
    const h = document.createElement('div');
    h.className = 'hl';
    Object.assign(h.style, { left: r.left - p + 'px', top: r.top - p + 'px',
      width: r.width + 2 * p + 'px', height: r.height + 2 * p + 'px' });
    if (opts.label) {
      const l = document.createElement('div');
      l.className = 'hl-label ' + (opts.side || 'below');
      l.textContent = opts.label;
      h.appendChild(l);
    }
    cur().appendChild(h);
    h.animate([{ opacity: 0, transform: 'scale(1.08)' }, { opacity: 1, transform: 'scale(1)' }],
      { duration: 450, delay: opts.delay ?? 0, easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'both' });
  };

  // Called by render.py after a step's changes are applied: pause every
  // animation that started in this step and report when the last one ends.
  window.prepare = () => {
    const known = new Set(window.__known || []);
    fresh = document.getAnimations().filter(a => !known.has(a));
    let end = 0;
    for (const a of fresh) {
      a.pause();
      const e = a.effect.getComputedTiming().endTime;
      if (Number.isFinite(e)) end = Math.max(end, e);
    }
    window.__known = document.getAnimations();
    return Math.min(end, 5000);
  };

  window.seek = (t) => { for (const a of fresh) a.currentTime = t; };
})();
