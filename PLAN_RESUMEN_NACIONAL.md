# Resumen nacional en vivo — encargo para una sesión en la nube

> Idea de Rodrigo (18-sep-2026): «para el futuro generaremos uno que será un resumen en vivo para todas
> las ciudades al mismo tiempo». Encargo escrito el 24-sep-2026 para ejecutarlo en una **sesión en la
> nube** (crédito de US$250 de sesiones cloud), porque no necesita el disco ni el procesador del
> notebook: todo lo que usa es **público por HTTP**. Todas las fuentes de abajo se verificaron ese día.

## Qué se construye

Un tablero **de una sola página**, estático (GitHub Pages), en un repositorio **nuevo e independiente**
(`romedinag-tech/transportepublicoChile`), que muestre **todas las ciudades en vivo al mismo tiempo**:
una tarjeta por ciudad con el estado de ahora contra lo normal de esa hora y ese tipo de día, y un
enlace al tablero de la ciudad. No reemplaza a ningún tablero de ciudad: es la puerta de entrada.

**Por qué repositorio nuevo:** los 19 tableros de ciudad se generan desde el kit compartido del motor
(`_motor/dashboard_kit/`, en el notebook) y cada deploy **sobrescribe** su `assets/`. Cualquier cambio
hecho a mano en esos repositorios se pierde en el próximo deploy. Este resumen no sale del kit, así que
vive aparte y no choca con nada.

## Fuentes (todas públicas, verificadas el 24-sep-2026)

**1. Vivo de cada ciudad** — `https://storage.googleapis.com/<bucket>/dia.json`
CORS abierto (`Access-Control-Allow-Origin: *`), `Cache-Control: public, max-age=30`. Refrescar cada 60 s.

**2. Lo normal de cada ciudad** — `https://romedinag-tech.github.io/<repo>/data/baseline_30min.json`

| slug | Ciudad | bucket | repo del tablero |
|---|---|---|---|
| gccp | Gran Concepción | `gccp-transporte-live` | `transportepublicoGC` |
| iquique | Iquique | `iquique-transporte-live` | `transportepublicoIquique` |
| tocopilla | Tocopilla | `tocopilla-transporte-live` | `transportepublicoTocopilla` |
| antofagasta | Antofagasta | `antofagasta-transporte-live` | ⚠ `transportepublicoantofagasta` (**minúsculas**; con mayúscula da 404) |
| calama | Calama | `calama-transporte-live` | `transportepublicoCalama` |
| copiapo | Copiapó | `copiapo-transporte-live` | `transportepublicoCopiapo` |
| valparaiso | Gran Valparaíso | `valparaiso-transporte-live` | `transportepublicoValparaiso` |
| rancagua | Rancagua | `rancagua-transporte-live` | `transportepublicoRancagua` |
| talca | Talca | `talca-transporte-live` | `transportepublicoTalca` |
| linares | Linares | `linares-transporte-live` | ⚠ **sin tablero** (sólo acumula vivo): tarjeta sin enlace y sin «normal» |
| chillan | Chillán | `chillan-transporte-live` | `transportepublicoChillan` |
| temuco | Temuco | `temuco-transporte-live` | `transportepublicoTemuco` |
| villarrica | Villarrica | `villarrica-transporte-live` | `transportepublicoVillarrica` |
| valdivia | Valdivia | `valdivia-transporte-live` | `transportepublicoValdivia` |
| osorno | Osorno | `osorno-transporte-live` | `transportepublicoOsorno` |
| castro | Castro | `castro-transporte-live` | `transportepublicoCastro` |
| quellon | Quellón | `quellon-transporte-live` | `transportepublicoQuellon` |
| punta_arenas | Punta Arenas | ⚠ `puntaarenas-transporte-live` (**sin guion bajo**) | `transportepublicoPuntaArenas` |

Orden de presentación: **norte a sur**, como arriba. Santiago no tiene vivo (su vivo es un web service
DTPM de acceso por solicitud): no se incluye, o va como tarjeta «sin vivo».

## Esquema que se usa

**`dia.json`** (una fila por ciudad, el día en curso): `fecha` (AAAA-MM-DD) · `snapshot` (ISO con zona
horaria: **hora de la última captura**) · `dia_tipo` (`L` laboral, `S` sábado, `D` domingo **o feriado**:
el capturador ya conoce el calendario de feriados) · `bin` (0–47, franja de 30 min del día) · `buses_op`
(buses en ruta) · `term` (en terminal) · `descanso` (fuera de servicio) · `inact` (sin operar hoy) ·
`flota` · `vel` (km/h) · `det` (% del tiempo detenido) · `freq` (salidas por hora) · `freq_serie` (48
franjas del día).

**`baseline_30min.json`**: `bins` (48 rótulos `"HH:MM"`) y un bloque por tipo de día `L`, `S`, `D`, cada
uno con series de 48 valores (`vel`, `det`, `freq`, `buses_op`…; pueden traer `null` fuera de horario).

**Lo normal de este momento** = `baseline[dia.dia_tipo][indicador][dia.bin]`. Es exactamente lo que hace
cada tablero de ciudad (`app_shell.js`: `const base = BASE30[DIA.dia_tipo] || {}, b = DIA.bin;`).

## Reglas que no se negocian

- **Privacidad:** usar sólo los agregados de sistema de arriba. `dia.json` trae además campos por línea
  y `excesos_geo`, que puede contener **posiciones de eventos individuales**: **no se usa ni se
  republica**. Nada de patentes ni coordenadas de buses.
- **Un solo archivo HTML** autocontenido: CSS y JS embebidos, librerías embebidas o de
  cdnjs/jsdelivr con verificación de carga. Nada de rutas a archivos locales.
- **Señal vencida se declara, no se esconde:** si `snapshot` tiene más de 10 minutos, o `fecha` no es la
  de hoy en Chile (`America/Santiago`), la tarjeta dice «sin señal desde HH:MM» en gris, en vez de
  mostrar números viejos como si fueran de ahora.
- **Feriado:** si `dia_tipo` es `D` en un día de semana, la tarjeta dice «feriado · se compara con
  domingo». Sin eso, un 18 de septiembre marca −60 % en todas las ciudades.
- **Una comparación sólo si hay base:** si lo normal de esa franja es `null` o 0, se muestra el valor sin
  porcentaje. Nunca dividir por cero ni inventar una base.
- **Estándar visual de Rodrigo:** modo claro y oscuro con toggle, mapa real (Leaflet) si se agrega un mapa
  de Chile con un punto por ciudad, cifras en formato chileno (coma decimal, punto de miles).

## Qué mostrar por ciudad (propuesta inicial, a validar con Rodrigo al primer borrador)

Buses en ruta (vs normal) · velocidad media (vs normal) · % detenido (vs normal) · salidas por hora (vs
normal) · hora de la última captura · enlace «abrir tablero». Arriba, una franja nacional: ciudades con
señal, buses en ruta sumados y las tres ciudades con mayor desvío contra lo normal.

## Cómo se verifica antes de entregar

- Servir por HTTP y medir en el navegador: 18 tarjetas renderizadas con superficie > 0, cada una con su
  `snapshot` leído del JSON de **esa** ciudad (no un valor repetido de otra).
- Contraste manual con dos tableros de ciudad abiertos a la vez: la misma cifra de «buses en ruta» y de
  «lo normal» a la misma hora.
- Probar la ruta de Antofagasta (minúsculas), el bucket de Punta Arenas y la tarjeta de Linares.
- Publicar con GitHub Pages por API y verificar HTTP 200 del sitio.
