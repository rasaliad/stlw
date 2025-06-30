# Comando /savepoint - Implementación

## 📝 Uso del Comando

Cuando el context left until auto-compact se esté agotando, simplemente escribe:

```
/savepoint
```

## 🤖 Respuesta Automática

Cuando recibas este comando, debes:

1. **Generar timestamp automático**
2. **Crear archivo savepoint con resumen completo**
3. **NO mostrar el contenido en pantalla**
4. **Confirmar solo la creación del archivo**

## 📋 Template del Comando

```markdown
# SAVEPOINT: Sistema STL - Warehouse Management System
**Fecha:** [TIMESTAMP_ACTUAL]
**Estado:** [ESTADO_ACTUAL_DEL_PROYECTO]

## 📋 RESUMEN EJECUTIVO
[Descripción del estado actual del proyecto]

## 🏗️ ARQUITECTURA TÉCNICA
[Stack tecnológico actual]

## 📁 ESTRUCTURA DE ARCHIVOS CLAVE
[Archivos importantes del proyecto]

## 🗄️ ESTRUCTURA DE BASE DE DATOS
[Tablas y datos actuales]

## ✅ MÓDULOS IMPLEMENTADOS
[Lista de funcionalidades completadas]

## 🔧 CONFIGURACIONES IMPORTANTES
[Variables de entorno y configuraciones clave]

## 🚀 COMANDOS ÚTILES
[Comandos para operar el sistema]

## 🐛 PROBLEMAS RESUELTOS
[Historial de bugs y soluciones]

## 📝 PENDIENTES
[Tareas por completar]

## 🎨 CARACTERÍSTICAS UI/UX
[Aspectos de diseño y experiencia]

## 🔄 ESTADO ACTUAL
[Resumen del estado funcional]

## 🔗 URLs DE ACCESO
[Enlaces importantes del sistema]

---
*Savepoint generado automáticamente*
```

## 🎯 Respuesta Tipo

Cuando recibas `/savepoint`, responde únicamente con:

```
Savepoint creado: /home/rasaliad/app/stlw/savepoint_[TIMESTAMP].md

✅ Estado del proyecto documentado exitosamente
📊 Módulos: X completados, Y pendientes  
🗂️ Datos: X registros sincronizados
🔧 Sistema: Funcional
```

## 📅 Formato de Timestamp

Usar formato: `YYYYMMDDHHMMSS`
Ejemplo: `20250629184750`

## 💡 Beneficios

- **Continuidad**: Permite retomar el proyecto sin pérdida de contexto
- **Documentación**: Historial automático de progreso
- **Eficiencia**: Comando rápido sin output verbose
- **Trazabilidad**: Cada savepoint marca un hito del desarrollo

## 🔄 Cuándo Usar

- Context left < 10%
- Antes de implementar cambios grandes
- Al completar módulos importantes
- Antes de cerrar sesiones de trabajo
- Cuando se necesite documentar estado actual

---
*Comando implementado para el proyecto STL*