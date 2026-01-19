(() => {
  const slider = document.getElementById("slider");
  if (!slider) return;

  const slides = Array.from(slider.querySelectorAll(".slide"));
  const prevBtn = slider.querySelector(".prev");
  const nextBtn = slider.querySelector(".next");
  const dotsWrap = slider.querySelector(".dots");

  let index = slides.findIndex(s => s.classList.contains("active"));
  if (index < 0) index = 0;

  // build dots
  dotsWrap.innerHTML = "";
  const dots = slides.map((_, i) => {
    const b = document.createElement("button");
    b.className = "dot" + (i === index ? " active" : "");
    b.type = "button";
    b.setAttribute("aria-label", `Go to slide ${i + 1}`);
    b.addEventListener("click", () => go(i, true));
    dotsWrap.appendChild(b);
    return b;
  });

  function render() {
    slides.forEach((s, i) => s.classList.toggle("active", i === index));
    dots.forEach((d, i) => d.classList.toggle("active", i === index));
  }

  function go(nextIndex, userAction = false) {
    index = (nextIndex + slides.length) % slides.length;
    render();
    if (userAction) restart();
  }

  function next(userAction = false) {
    go(index + 1, userAction);
  }

  function prev(userAction = false) {
    go(index - 1, userAction);
  }

  prevBtn?.addEventListener("click", () => prev(true));
  nextBtn?.addEventListener("click", () => next(true));

  // auto play
  let timer = null;
  const intervalMs = 3500;

  function start() {
    if (timer) return;
    timer = setInterval(() => next(false), intervalMs);
  }

  function stop() {
    if (!timer) return;
    clearInterval(timer);
    timer = null;
  }

  function restart() {
    stop();
    start();
  }

  slider.addEventListener("mouseenter", stop);
  slider.addEventListener("mouseleave", start);

  // init
  render();
  start();
})();
