/* Copy-credit buttons on the /pictures page. Each button carries its
   suggested credit line in data-credit; clicking copies it and flashes
   confirmation on the button label. Without JS the buttons do nothing,
   but the credit line is printed on the card either way. */
(function () {
    "use strict";

    function flash(button, label) {
        var original = button.innerHTML;
        button.innerHTML = label;
        button.classList.add("is-copied");
        button.disabled = true;
        setTimeout(function () {
            button.innerHTML = original;
            button.classList.remove("is-copied");
            button.disabled = false;
        }, 1600);
    }

    function fallbackCopy(text) {
        var scratch = document.createElement("textarea");
        scratch.value = text;
        scratch.setAttribute("readonly", "");
        scratch.style.position = "absolute";
        scratch.style.left = "-9999px";
        document.body.appendChild(scratch);
        scratch.select();
        var ok = false;
        try {
            ok = document.execCommand("copy");
        } catch (e) {
            ok = false;
        }
        document.body.removeChild(scratch);
        return ok;
    }

    function wire() {
        document.querySelectorAll(".picture-copy").forEach(function (button) {
            button.addEventListener("click", function () {
                var credit = button.getAttribute("data-credit");
                var copied = '<i class="fa-solid fa-check" aria-hidden="true"></i> Copied';
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(credit).then(
                        function () { flash(button, copied); },
                        function () {
                            if (fallbackCopy(credit)) { flash(button, copied); }
                        }
                    );
                } else if (fallbackCopy(credit)) {
                    flash(button, copied);
                }
            });
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", wire);
    } else {
        wire();
    }
})();
