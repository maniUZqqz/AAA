/* ناوبری ارائه — کیبورد، سلکتور، سوایپ */
(function () {
  "use strict";

  var prev = document.querySelector('a[rel="prev"]:not(.off)');
  var next = document.querySelector('a[rel="next"]:not(.off)');
  var jump = document.getElementById("jump");

  function go(link) { if (link) window.location.href = link.href; }

  /* RTL: فلش چپ یعنی جلو، فلش راست یعنی عقب */
  document.addEventListener("keydown", function (e) {
    if (e.ctrlKey || e.altKey || e.metaKey) return;
    if (document.activeElement === jump) return;

    switch (e.key) {
      case "ArrowLeft":
      case "PageDown":
      case " ":
        e.preventDefault(); go(next); break;
      case "ArrowRight":
      case "PageUp":
        e.preventDefault(); go(prev); break;
      case "Home":
        e.preventDefault(); window.location.href = "/slide/1"; break;
      case "End":
        e.preventDefault();
        window.location.href = "/slide/" + jump.options.length; break;
      case "f":
      case "F":
        e.preventDefault();
        if (document.fullscreenElement) document.exitFullscreen();
        else document.documentElement.requestFullscreen();
        break;
    }
  });

  if (jump) {
    jump.addEventListener("change", function () {
      window.location.href = "/slide/" + this.value;
    });
  }

  /* سوایپ روی موبایل */
  var x0 = null;
  addEventListener("touchstart", function (e) { x0 = e.changedTouches[0].clientX; }, { passive: true });
  addEventListener("touchend", function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    x0 = null;
    if (Math.abs(dx) < 60) return;
    go(dx < 0 ? prev : next);   /* RTL */
  }, { passive: true });

  /* ویدیوهای نمونه‌کار وقتی دیده شدند پخش شوند */
  var vids = document.querySelectorAll("video[data-auto]");
  if (vids.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) en.target.play().catch(function () {});
        else en.target.pause();
      });
    }, { threshold: 0.35 });
    vids.forEach(function (v) { io.observe(v); });
  }
})();
