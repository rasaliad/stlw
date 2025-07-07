# STL Telegram Bot

Bot de notificaciones para el sistema STL Warehouse Management.

## Características

- 🔔 Notificaciones automáticas de eventos del sistema STL
- 👥 Sistema de usuarios con verificación por código
- 📊 Consultas de información en tiempo real
- 🔐 Control de acceso y suscripciones

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con las configuraciones necesarias
```

## Configuración

1. **Base de datos**: Configurar conexión a la BD de STL
2. **Bot Token**: Obtener token de @BotFather en Telegram
3. **Variables de entorno**: Configurar `.env`

## Uso

```bash
python main.py
```

## Comandos del Bot

- `/start` - Registrar usuario
- `/vincular <código>` - Vincular con usuario del sistema
- `/status` - Ver estado de cuenta
- `/suscribir <tipo>` - Suscribirse a notificaciones
- `/consultar <tipo> <valor>` - Realizar consultas
- `/help` - Ver ayuda completa

## Arquitectura

El bot funciona como un servicio independiente que:
1. Monitorea la cola de notificaciones en la BD
2. Procesa mensajes pendientes
3. Envía notificaciones a usuarios suscritos
4. Permite consultas directas via comandos

## Desarrollo

Para desarrollo local, usar `python main.py --debug`