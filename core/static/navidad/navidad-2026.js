/* ===========================================================================
   NAVIDAD 2026 (v2, 17-11-2026) -- Punto Parcelas
   ---------------------------------------------------------------------------
   La decoracion la decide el SERVIDOR (core.context_processors.navidad): la
   franja, la guirnalda y los gorros llegan en el HTML desde el primer pintado
   y funcionan sin JS. Este script solo hace lo que el HTML no puede:

   1. Nieve que cae, en las portadas (.hero, .catalog-hero, .reserva-hero),
      DETRAS del texto y los botones. Nunca en el catalogo de fotos, las fichas
      ni el formulario. No corre si se pidio menos movimiento.
   2. Se apaga sola si alguien deja la pestana abierta al terminar la ventana.
      La cuenta regresiva viene del servidor (data-navidad-falta, en ms), asi
      que no depende de que el reloj del computador este bien.
   3. Si la pagina abre ya bajada (recarga a media pagina), deja el menu en su
      estado compacto de una vez.
   =========================================================================== */
(function () {
  "use strict";
  var raiz = document.documentElement;
  if (!raiz.classList.contains("pp-navidad")) return;

  var alApagar = [];
  function apagar() {
    raiz.classList.remove("pp-navidad");
    for (var i = 0; i < alApagar.length; i++) alApagar[i]();
    alApagar = [];
  }

  // --- 2. Apagado con la pestana abierta (revisa como mucho una vez al dia;
  //        setTimeout no acepta esperas de mas de 24 dias). ------------------
  var falta = parseInt(raiz.getAttribute("data-navidad-falta"), 10);
  if (falta > 0 && window.performance) {
    var fin = performance.now() + falta;
    (function vigilar() {
      var resto = fin - performance.now();
      if (resto <= 0) { apagar(); return; }
      setTimeout(vigilar, Math.min(resto + 500, 86400000));
    })();
  }

  // --- 3. Menu compacto si la pagina abre ya bajada. -------------------------
  var menu = document.getElementById("ppNav");
  if (menu && window.scrollY > 40) menu.classList.add("scrolled");

  // --- 1. Nieve --------------------------------------------------------------
  // Menos movimiento pedido al sistema: sin nieve. A algunas personas el
  // movimiento les da mareo o migrana; no quitar esto para "que se vea".
  var quieto = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  if (quieto && quieto.matches) return;

  var portadas = document.querySelectorAll(".hero, .catalog-hero, .reserva-hero");
  for (var p = 0; p < portadas.length; p++) nevar(portadas[p]);

  function nevar(portada) {
    var lienzo = document.createElement("canvas");
    var ctx = lienzo.getContext ? lienzo.getContext("2d") : null;
    if (!ctx) return;
    lienzo.className = "pp-nieve";
    lienzo.setAttribute("aria-hidden", "true");
    // Estilo propio por si el CSS no cargo: nunca ocupa lugar ni recibe toques.
    lienzo.style.cssText = "position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none;";
    // Justo antes del contenido (que tiene z-index 1): la nieve cae detras del
    // titulo y de los botones, por encima de la foto de fondo.
    var contenido = null;
    for (var c = 0; c < portada.children.length; c++) {
      if (/hero-content/.test(portada.children[c].className)) { contenido = portada.children[c]; break; }
    }
    portada.insertBefore(lienzo, contenido);

    var escala = Math.min(window.devicePixelRatio || 1, 2);
    var ancho = 0, alto = 0, copos = [];
    var visible = true, corriendo = false, parado = false, ultimo = 0;

    // Copos dibujados una vez y reutilizados: cristales de seis brazos de
    // varios tamanos (algunos dorados, como la marca) y puntos suaves.
    function cristal(r, color) {
      var lado = Math.ceil((r * 2 + 4) * escala), s = document.createElement("canvas");
      s.width = s.height = lado;
      var g = s.getContext("2d"), m = lado / 2, R = r * escala;
      g.strokeStyle = color;
      g.lineCap = "round";
      g.lineWidth = Math.max(1, r / 4.5) * escala;
      g.beginPath();
      for (var k = 0; k < 6; k++) {
        var a = k * Math.PI / 3, ca = Math.cos(a), sa = Math.sin(a);
        g.moveTo(m, m);
        g.lineTo(m + ca * R, m + sa * R);
        var bx = m + ca * R * 0.55, by = m + sa * R * 0.55, L = R * 0.35;
        for (var lado2 = -1; lado2 <= 1; lado2 += 2) {
          var b = a + lado2 * Math.PI / 4;
          g.moveTo(bx, by);
          g.lineTo(bx + Math.cos(b) * L, by + Math.sin(b) * L);
        }
      }
      g.stroke();
      return { img: s, tam: lado / escala, gira: true };
    }
    function punto(r) {
      var lado = Math.ceil((r * 2 + 2) * escala), s = document.createElement("canvas");
      s.width = s.height = lado;
      var g = s.getContext("2d"), m = lado / 2;
      var grad = g.createRadialGradient(m, m, 0, m, m, m);
      grad.addColorStop(0, "rgba(255,253,246,1)");
      grad.addColorStop(0.55, "rgba(255,253,246,.85)");
      grad.addColorStop(1, "rgba(255,253,246,0)");
      g.fillStyle = grad;
      g.fillRect(0, 0, lado, lado);
      return { img: s, tam: lado / escala, gira: false };
    }
    var CREMA = "rgba(255,252,242,1)", ORO = "rgba(240,206,96,1)";
    var cristales = [cristal(4.5, CREMA), cristal(6, CREMA), cristal(7.5, CREMA), cristal(9.5, CREMA),
                     cristal(5.5, ORO), cristal(7.5, ORO)];
    var puntos = [punto(1.6), punto(2.3), punto(3.2)];

    function nuevo(enCualquierAltura) {
      var esCristal = Math.random() < 0.32;
      var sp = esCristal ? cristales[Math.floor(Math.random() * cristales.length)]
                         : puntos[Math.floor(Math.random() * puntos.length)];
      return {
        sp: sp,
        x: Math.random() * ancho,
        y: enCualquierAltura ? Math.random() * alto : -sp.tam,
        v: (esCristal ? 22 : 30) + sp.tam * 2.2 + Math.random() * 18,   // px por segundo
        fase: Math.random() * Math.PI * 2,
        vaiven: 10 + Math.random() * 22,
        rot: Math.random() * Math.PI,
        giro: (Math.random() - 0.5) * 1.2,
        a: esCristal ? 0.75 + Math.random() * 0.25 : 0.45 + Math.random() * 0.45
      };
    }

    // La nieve nace en la guirnalda: el lienzo empieza bajo el menu, para que
    // ningun copo pase por detras de los enlaces del menu y les quite lectura.
    function techo() {
      var cuelga = parseFloat(getComputedStyle(raiz).getPropertyValue("--pp-cuelga")) || 0;
      return Math.round((menu ? menu.offsetHeight : 0) + cuelga * 0.4);
    }

    function medir() {
      var arriba = techo();
      var w = portada.clientWidth, h = Math.max(0, portada.clientHeight - arriba);
      if (w === ancho && h === alto) return;    // la barra del celular no obliga a redibujar
      ancho = w; alto = h;
      lienzo.style.top = arriba + "px";
      lienzo.style.height = alto + "px";
      lienzo.width = Math.round(ancho * escala);
      lienzo.height = Math.round(alto * escala);
      ctx.setTransform(escala, 0, 0, escala, 0, 0);
      var cuantos = Math.round(Math.min(130, Math.max(30, ancho / 14)));
      while (copos.length < cuantos) copos.push(nuevo(true));
      copos.length = cuantos;
    }

    function cuadro(t) {
      if (!corriendo) return;
      var dt = Math.min(0.05, ((t - ultimo) / 1000) || 0);
      ultimo = t;
      ctx.clearRect(0, 0, ancho, alto);
      for (var i = 0; i < copos.length; i++) {
        var f = copos[i];
        f.y += f.v * dt;
        f.fase += dt * 0.8;
        f.rot += f.giro * dt;
        if (f.y > alto + f.sp.tam) { copos[i] = nuevo(false); continue; }
        var x = f.x + Math.sin(f.fase) * f.vaiven, t2 = f.sp.tam;
        ctx.globalAlpha = f.a;
        if (f.sp.gira) {
          ctx.save();
          ctx.translate(x, f.y);
          ctx.rotate(f.rot);
          ctx.drawImage(f.sp.img, -t2 / 2, -t2 / 2, t2, t2);
          ctx.restore();
        } else {
          ctx.drawImage(f.sp.img, x - t2 / 2, f.y - t2 / 2, t2, t2);
        }
      }
      ctx.globalAlpha = 1;
      window.requestAnimationFrame(cuadro);
    }

    function arrancar() {
      if (parado || corriendo || !visible || document.hidden) return;
      corriendo = true;
      ultimo = performance.now();
      window.requestAnimationFrame(cuadro);
    }
    function parar() {
      parado = true;
      corriendo = false;
      if (lienzo.parentNode) lienzo.parentNode.removeChild(lienzo);
    }
    alApagar.push(parar);

    medir();
    // Solo anima mientras la portada se ve: al bajar a leer no gasta bateria
    // ni le quita fluidez al scroll del celular.
    if (window.IntersectionObserver) {
      new IntersectionObserver(function (entradas) {
        visible = entradas[entradas.length - 1].isIntersecting;   // la ultima es la vigente
        if (visible) arrancar(); else corriendo = false;
      }).observe(portada);
    }
    arrancar();
    window.addEventListener("resize", medir, { passive: true });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) corriendo = false; else arrancar();
    });
    if (quieto) {
      var alCambiar = function () { if (quieto.matches) parar(); };
      if (quieto.addEventListener) quieto.addEventListener("change", alCambiar);
      else if (quieto.addListener) quieto.addListener(alCambiar);
    }
  }
})();
