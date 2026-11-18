// Tema claro/escuro: guardado no browser (só preferência de quem vê)
(function () {
  var raiz = document.documentElement;
  var btn = document.getElementById("alternar-tema");
  if (btn) {
    btn.addEventListener("click", function () {
      var claro = raiz.getAttribute("data-tema") !== "claro";
      raiz.setAttribute("data-tema", claro ? "claro" : "escuro");
      try { localStorage.setItem("tema", claro ? "claro" : "escuro"); } catch (e) {}
    });
  }

  // Menu em ecrãs pequenos
  var menu = document.getElementById("abrir-menu");
  if (menu) {
    menu.addEventListener("click", function () {
      var aberta = menu.closest(".sidebar").classList.toggle("aberta");
      menu.setAttribute("aria-expanded", aberta ? "true" : "false");
    });
  }

  // Nova encomenda: acrescentar e remover trabalhos
  var lista = document.getElementById("trabalhos");
  var modelo = document.getElementById("modelo-trabalho");
  var adicionar = document.getElementById("adicionar-trabalho");
  if (lista && modelo && adicionar) {
    var proximo = lista.querySelectorAll(".trabalho-bloco").length;
    var renumerar = function () {
      lista.querySelectorAll(".trabalho-bloco").forEach(function (b, i) {
        var t = b.querySelector(".numero-trabalho");
        if (t) t.textContent = "Trabalho " + String(i + 1).padStart(2, "0");
        var r = b.querySelector(".remover-trabalho");
        if (r) r.hidden = lista.querySelectorAll(".trabalho-bloco").length === 1;
      });
    };
    adicionar.addEventListener("click", function () {
      var html = modelo.innerHTML.replace(/__i__/g, String(proximo++));
      var tmp = document.createElement("div");
      tmp.innerHTML = html.trim();
      lista.appendChild(tmp.firstChild);
      renumerar();
    });
    lista.addEventListener("click", function (ev) {
      if (ev.target.closest(".remover-trabalho")) {
        ev.target.closest(".trabalho-bloco").remove();
        renumerar();
      }
    });
    renumerar();
  }

  // Confirmação simples em botões com data-confirmar
  document.querySelectorAll("[data-confirmar]").forEach(function (el) {
    el.addEventListener("click", function (ev) {
      if (!window.confirm(el.getAttribute("data-confirmar"))) ev.preventDefault();
    });
  });
})();
