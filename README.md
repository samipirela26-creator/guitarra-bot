# Trivilín — bot de práctica de guitarra

Bot de Telegram para practicar cambios de tonalidad, consultar el círculo de quintas
y recibir tarjetas de práctica (acordes + rasgueo + tiempo). Personalidad: Trivilín,
el Perro del Saxo.

## Comandos

- `/start`, `/help`
- `/practicar` — juego: te da una progresión en un tono, la transportas a otro tono
  y eliges la opción correcta entre botones.
- `/circulo` — imagen del círculo de quintas con las relativas menores.
- `/tarjeta` — tarjeta con diagramas de acordes, patrón de rasgueo y BPM sugerido.
- `/puntaje` — racha actual y mejor racha.

## Cómo correrlo

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # completar TELEGRAM_BOT_TOKEN y ALLOWED_USER_IDS
.venv/bin/python main.py
```

## Estructura

- `src/theory/` — motor de teoría musical puro (transposición, círculo de quintas,
  progresiones diatónicas, ritmo). Sin dependencias de Telegram ni de Pillow.
- `src/graphics/` — todo lo que dibuja imágenes con Pillow (diagramas de acordes,
  círculo de quintas, tarjetas de práctica).
- `src/bot/handlers.py` — comandos y callbacks de Telegram.
- `src/db.py` — puntaje/racha en SQLite (`guitarra.db`, no se sube a git).
- `assets/circulo_quintas.png` — se genera la primera vez que se pide `/circulo`
  (cacheada en disco, no se sube a git).

## Notas de diseño

- Las digitaciones de acordes (`src/theory/chord_shapes.py`) cubren las 12
  tonalidades mayores y menores usadas por las progresiones diatónicas
  (`src/theory/progressions.py` solo genera acordes mayores y menores, nunca
  disminuidos, así que no hace falta digitación para acordes dim).
- El juego de `/practicar` guarda el índice de la respuesta correcta directo en
  el `callback_data` del botón (`ans|elegido|correcto`) en vez de guardar estado
  del lado del servidor — más simple y suficiente para un bot de un solo usuario.
