/* Data Insight chart export.
   Wires any [data-export-target] button to render its target figure to a PNG
   via the vendored html-to-image (lib/html-to-image.min.js). ES5, no build step.
   Mobile-friendly: uses a Blob object URL and the Web Share sheet when available,
   since mobile Safari ignores the data-URL download trick. */
(function () {
  if (!window.htmlToImage) { return; }

  var buttons = document.querySelectorAll('[data-export-target]');
  for (var i = 0; i < buttons.length; i++) {
    wire(buttons[i]);
  }

  function wire(btn) {
    btn.addEventListener('click', function () {
      var node = document.querySelector(btn.getAttribute('data-export-target'));
      if (!node) { return; }
      var fname = (btn.getAttribute('data-export-name') || 'chart') + '.png';
      var label = btn.textContent;
      btn.textContent = 'Rendering…';
      btn.disabled = true;

      window.htmlToImage.toPng(node, {
        pixelRatio: 2,
        backgroundColor: '#fbfbfc',
        // keep the interactive toggle chips out of the exported image
        filter: function (n) {
          return !(n.classList && n.classList.contains('di-toggle'));
        }
      }).then(function (dataUrl) {
        return fetch(dataUrl);
      }).then(function (res) {
        return res.blob();
      }).then(function (blob) {
        var file = null;
        try { file = new File([blob], fname, { type: 'image/png' }); } catch (e) { file = null; }
        // Mobile: open the native share sheet (Save Image / share) when possible.
        if (file && navigator.canShare && navigator.canShare({ files: [file] })) {
          return navigator.share({ files: [file] }).catch(function () { openInNewTab(blob); });
        }
        // Desktop: download via an object URL.
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = fname;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
      }).catch(function (err) {
        console.error('PNG export failed', err);
      }).then(function () {
        btn.textContent = label;
        btn.disabled = false;
      });
    });
  }

  // Fallback for mobile browsers without Web Share: show the image so the user
  // can long-press and save it.
  function openInNewTab(blob) {
    var url = URL.createObjectURL(blob);
    var w = window.open();
    if (w) { w.location.href = url; }
  }
})();
