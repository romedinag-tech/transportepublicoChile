# Transporte público de Chile — resumen nacional en vivo

## Propósito

Una sola página que muestra el transporte público regional de Chile **en vivo, todas las ciudades a la
vez**: una tarjeta por ciudad con el estado de ahora contra lo normal de esa hora y ese tipo de día, y el
enlace al tablero de cada ciudad. Es la puerta de entrada a los 19 tableros de ciudad.

## Estado

activo
Recién creado (2026-09-24). El encargo completo, con fuentes verificadas, esquemas y reglas, está en
[`PLAN_RESUMEN_NACIONAL.md`](PLAN_RESUMEN_NACIONAL.md). **Leerlo entero antes de escribir código.**

## Entradas y salidas

**Consume** (todo público por HTTP, nada local): el vivo de cada ciudad en
`https://storage.googleapis.com/<bucket>/dia.json` y lo normal en
`https://romedinag-tech.github.io/<repo>/data/baseline_30min.json`. La tabla ciudad → bucket → repo
está en el encargo.

**Produce:** `index.html` autocontenido, publicado con GitHub Pages en
`https://romedinag-tech.github.io/transportepublicoChile/`.

## Datos canónicos

No hay datos propios: todo se lee en vivo desde las fuentes de arriba. Este repositorio no guarda ni
copia datos de las ciudades.

## Aprendizajes

- **2026-09-24 — Tres nombres que no siguen la regla** (verificados por HTTP): el tablero de Antofagasta
  es `transportepublicoantofagasta` en **minúsculas** (con mayúscula da 404); el bucket de Punta Arenas es
  `puntaarenas-transporte-live`, **sin guion bajo**; Linares **no tiene tablero** (sólo acumula vivo).
- **El «normal» depende del tipo de día, y el feriado es `D`.** El capturador ya clasifica los feriados
  como domingo. Comparar un feriado contra un día laboral fabricó caídas de −60 % en todas las ciudades el
  18-sep-2026.
- **La privacidad se audita por contenido.** `dia.json` trae `excesos_geo`, que puede tener posiciones de
  eventos individuales. No se usa ni se republica.

## Cómo se ejecuta

Sitio estático: abrir `index.html` servido por HTTP (`python -m http.server`), nunca con `file://`.

---

## Cómo trabaja Rodrigo (vale para esta sesión)

Rodrigo Medina es ingeniero de transporte urbano, ex secretario ejecutivo de SECTRA. **Tutéalo, en
español de Chile.** No le expliques lo que es del oficio; lo que espera es que las cifras estén medidas.

- **No inventar.** Ninguna cifra de memoria: se lee del archivo en el momento. Si una fuente no trae un
  dato, se muestra vacío y se dice, no se rellena.
- **Verificar el hecho, no la forma.** Una página no se verifica contando nodos del DOM: se mide que cada
  tarjeta tenga superficie > 0 con `getBoundingClientRect()` y que su cifra venga del JSON de **esa**
  ciudad. Contrastar al menos dos ciudades contra su propio tablero a la misma hora.
- **Nunca descartar en silencio.** Una ciudad sin señal o con dato vencido se muestra como tal, con la hora
  de la última captura.
- **Privacidad, piso innegociable:** nada de patentes ni coordenadas de buses individuales en lo publicado.
- **Un entregable es un archivo.** HTML autocontenido; librerías sólo de cdnjs o jsdelivr, con verificación
  de carga.
- **Formato chileno** en todas las cifras: coma decimal, punto de miles.
- **Modo claro y oscuro** con toggle; los gráficos releen los colores al cambiar de tema.
- **Pocas preguntas, afiladas.** Si una decisión cambia el diseño, se pregunta; lo rutinario se decide y se
  informa.
- **Publicar al cerrar un bloque**, con cache-bust (`?v=N`) para que no se vea la versión vieja.
