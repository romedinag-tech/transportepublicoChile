# Transporte público de Chile

Tablero público con datos resumen del transporte público por ciudad y buses en ruta en este momento. Versión de trabajo.

Sólo publica agregados por ciudad: no incluye patentes, posiciones de buses individuales ni microdato.

- `site/` es lo único que se publica.
- `scripts/vivo.py` actualiza el dato en vivo cada 30 minutos por GitHub Actions.
- `build/` arma la página desde los agregados.
