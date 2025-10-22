# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**STL Warehouse Management System** - A fullstack application integrating a Next.js 14 frontend with a FastAPI backend, connecting to an existing Firebird 2.5 database on Windows, and synchronizing bidirectionally with SAP via the SAP-STL API.

## Core Architecture

### Technology Stack
- **Backend**: FastAPI (Python 3.12) with `fdb` (Firebird driver)
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Database**: Firebird 2.5 (external, not containerized)
- **Containerization**: Docker Compose for development
- **Integration**: SAP-STL API via cloudflare tunnels
- **Notifications**: Telegram Bot (standalone Python service)

### Key Design Patterns

1. **Bidirectional Sync Architecture**:
   - **SAP → STL (GET)**: Scheduled sync pulls Items, Orders/Dispatches, and GoodsReceipts from SAP into local Firebird tables (STL_ITEMS, STL_DISPATCHES, STL_GOODS_RECEIPTS)
   - **STL → SAP (POST)**: Views (`vw_pedidos_to_sap`, `vw_recepcion_to_sap`) filter local data ready for SAP, then POST to `/Transaction/DeliveryNotes` and `/Transaction/GoodsReceipt`
   - **Unique Keys**: `numeroBusqueda + tipoDespacho` for dispatches, `numeroBusqueda + tipoRecepcion` for receipts (NOT numeroDespacho/numeroDocumento)
   - **Optimization**: MD5 hash checking to avoid redundant updates

2. **Database Connection Pattern**:
   - `FirebirdConnection` class in `app/core/database.py` provides context manager for connections
   - Always use `with db.get_connection() as conn:` pattern
   - Manual transaction management (commit/rollback)

3. **SAP-STL Client**:
   - Singleton instance `sap_stl_client` in `app/services/sap_stl_client.py`
   - JWT token authentication with auto-refresh
   - Mock mode (`USE_MOCK_SAP_DATA=true`) for development without external API
   - Async/await pattern for all API calls

4. **Sync Configuration**:
   - Tables: `STL_SYNC_CONFIG` (entity settings), `STL_SYNC_LOG` (operation history)
   - Each entity type (items, dispatches, goods_receipts) has configurable sync intervals
   - Background service runs scheduled tasks via APScheduler

5. **Telegram Bot Integration**:
   - Separate service in `stl-telegram-bot/` directory
   - Tables: `STL_TELEGRAM_USERS`, `STL_TELEGRAM_SUBSCRIPTIONS`, `STL_TELEGRAM_QUEUE`
   - Notifications sent on successful/failed SAP POST operations
   - Users must be verified by admin before receiving messages

## Common Development Commands

### Docker Operations
```bash
# Start all services (development mode with hot reload)
docker-compose up --build

# Start in background
docker-compose up -d --build

# View logs
docker-compose logs -f
docker-compose logs -f backend

# Rebuild specific service
docker-compose up --build backend

# Stop services
docker-compose down

# Clean everything
docker-compose down -v --remove-orphans

# Execute commands inside containers
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Backend Development
```bash
# Local development (without Docker)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run from project root
python -m uvicorn backend.app.main:app --reload
```

### Frontend Development
```bash
# Local development (without Docker)
cd frontend
npm install
npm run dev

# Build for production
npm run build
npm start

# Lint
npm run lint
```

### Telegram Bot
```bash
cd stl-telegram-bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Important URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Database Schema Critical Points

### SAP Sync Tables
- **STL_ITEMS**: Product master data (unique on `CODIGO_PRODUCTO`)
- **STL_DISPATCHES**: Order headers with `NUMERO_BUSQUEDA` (search key) and `TIPO_DESPACHO`
- **STL_DISPATCH_LINES**: Order line items (FK to STL_DISPATCHES)
- **STL_GOODS_RECEIPTS**: Receipt headers with `NUMERO_BUSQUEDA` and `TIPO_RECEPCION`
- **STL_GOODS_RECEIPT_LINES**: Receipt line items (FK to STL_GOODS_RECEIPTS)
- All have `SYNC_STATUS` ('PENDING', 'SYNCED', 'ERROR') and `LAST_SYNC_AT`

### Local Transaction Tables
- **pedidos**: Local orders with `estatus` (1=Pending, 2=InProcess, 3=Completed) and `estatus_erp` (1=NotSent, 2=ReadyToSend, 3=Sent)
- **recepciones**: Local receipts with same status pattern
- Views filter by `estatus = 3 AND estatus_erp = 2` to identify records ready for SAP

### Critical Indexes
- `IDX_STL_ITEMS_CODIGO` (unique)
- `IDX_STL_DISPATCH_SYNC`, `IDX_STL_RECEIPT_SYNC` for sync queries
- `IDX_STL_SYNC_LOG_ENTITY` for audit queries

## Configuration & Environment

### Required Environment Variables (.env)
```bash
# JWT
SECRET_KEY=<long-random-string>

# Firebird Database
FIREBIRD_HOST=host.docker.internal  # Use this in Docker, or 172.19.176.1 from WSL
FIREBIRD_PORT=3050
FIREBIRD_DATABASE=C:\\App\\STL\\Datos\\DATOS_STL.FDB
FIREBIRD_USER=sysdba
FIREBIRD_PASSWORD=masterkey

# SAP-STL API
SAP_STL_URL=https://contribute-pathology-price-spelling.trycloudflare.com
SAP_STL_USERNAME=STLUser
SAP_STL_PASSWORD=7a6T9IVeUdf5bvRIv
USE_MOCK_SAP_DATA=false  # Set to 'true' for development without external API

# Timezone
TZ=America/Santo_Domingo
```

### Network Configuration
- **Docker to Windows Firebird**: Use `host.docker.internal:3050`
- **WSL to Windows Firebird**: Use `172.19.176.1:3050` (or your vEthernet adapter IP)

## Key API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Returns JWT token
- `GET /api/v1/auth/me` - Current user info

### Sync Configuration
- `GET /api/v1/sync-config` - List all entity configurations
- `PUT /api/v1/sync-config/{entity_type}` - Update sync settings
- `GET /api/v1/sync-config/status` - Overall sync status

### SAP Synchronization
- `POST /api/sap-stl/sync/items` - Sync items from SAP
- `POST /api/sap-stl/sync/dispatches` - Sync dispatches from SAP
- `POST /api/sap-stl/sync/goods_receipts` - Sync receipts from SAP
- `GET /api/sap-stl/sync-now` - Trigger full sync
- `GET /api/sap-stl/test-connection` - Test SAP API connectivity

### Sending to SAP
- `POST /api/v1/sap/delivery/send-pending-deliveries?dry_run=true` - Send delivery notes to SAP
- `POST /api/v1/sap/goods-receipt/send-pending-receipts?dry_run=true` - Send goods receipts to SAP
- Use `dry_run=true` for testing without actual POST to SAP

### Telegram Bot
- `GET /api/v1/telegram/config` - Bot configuration
- `GET /api/v1/telegram/users` - List registered Telegram users
- `POST /api/v1/telegram/users/{id}/activate` - Activate user for notifications
- `GET /api/v1/telegram/bot-status` - Check bot health

## Important Coding Patterns

### Error Handling
- Always wrap Firebird operations in try/except with rollback
- Log errors with `logger.error()` including stack trace
- Return structured responses: `{"success": bool, "message": str, "data": any}`

### Date/Time Handling
- SAP API expects ISO format: `2025-01-06T00:00:00Z`
- Firebird stores `TIMESTAMP` type
- Python uses `datetime.datetime` objects
- Always be timezone-aware when comparing token expiry

### Async/Await
- SAP client methods are all async (must use `await`)
- Background sync service uses APScheduler for scheduled tasks
- Frontend API calls use axios with async/await

### Pydantic Models
- Located in `app/models/sap_stl_models.py` and `app/schemas/user.py`
- Use `.dict()` to serialize for JSON
- Models validate API request/response data automatically

## Windows Server Deployment

- **Encoding Issue**: Windows cmd uses cp1252, avoid emojis in logs
- Use `docker-compose.server.yml` or `docker-compose.windows.yml` for production
- Batch files provided: `deploy-windows-server.bat`, `start-backend-windows.bat`
- Installation guide: `INSTALACION_WINDOWS.md`, `README-WINDOWS.md`

## Testing & Debugging

### Mock Mode for SAP
Set `USE_MOCK_SAP_DATA=true` to use predefined JSON responses from `app/services/mock_sap_stl_service.py` instead of calling external API.

### Dry Run Mode
POST endpoints accept `?dry_run=true` to preview what would be sent without actually posting to SAP.

### Health Checks
- Backend: `curl http://localhost:8000/health`
- Frontend: `curl http://localhost:3000`

### Database Queries
Connect to Firebird with FlameRobin or isql:
```bash
isql -u sysdba -p masterkey localhost:3050/C:\App\STL\Datos\DATOS_STL.FDB
```

## Common Pitfalls

1. **Unique Keys**: Always use `numeroBusqueda + tipo` combo, NOT `numeroDespacho` or `numeroDocumento`
2. **Firebird Syntax**: Use `GEN_ID(generator_name, 1)` for auto-increment, not SERIAL
3. **Network**: Ensure Firebird port 3050 is open in Windows firewall
4. **Docker Host**: Use `host.docker.internal` not `localhost` to reach Windows services
5. **Commit Transactions**: Firebird requires explicit `conn.commit()`, it won't auto-commit
6. **Token Refresh**: SAP token has expiry, client auto-refreshes but check `token_expiry` timezone issues
7. **Shadcn DialogTitle**: Some components missing DialogTitle/DialogDescription, add them when editing dialogs

## File Structure Reference

```
stlw/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/      # Route handlers
│   │   │   │   ├── auth.py
│   │   │   │   ├── manual_dispatch.py
│   │   │   │   ├── sap_delivery.py
│   │   │   │   ├── sap_goods_receipt.py
│   │   │   │   ├── stl_pedidos.py
│   │   │   │   └── ...
│   │   │   └── v1/endpoints/   # Versioned API endpoints
│   │   ├── core/
│   │   │   ├── config.py       # Settings with pydantic-settings
│   │   │   ├── database.py     # FirebirdConnection class
│   │   │   └── security.py     # JWT & password hashing
│   │   ├── models/             # Pydantic models for SAP data
│   │   ├── schemas/            # Pydantic schemas for validation
│   │   ├── services/
│   │   │   ├── sap_stl_client.py          # SAP API client
│   │   │   ├── sap_stl_sync_service.py    # Sync from SAP to STL
│   │   │   ├── sap_delivery_service.py    # Send deliveries to SAP
│   │   │   ├── sap_goods_receipt_service.py # Send receipts to SAP
│   │   │   ├── background_sync_service.py # APScheduler tasks
│   │   │   └── telegram_bot_service.py    # Telegram integration
│   │   └── main.py             # FastAPI app initialization
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js 14 app router
│   │   │   ├── dashboard/
│   │   │   ├── despachos/
│   │   │   ├── recepciones/
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   └── ui/             # shadcn/ui components
│   │   └── lib/
│   │       └── api.ts          # Axios client with auth
│   ├── Dockerfile
│   └── package.json
├── stl-telegram-bot/           # Standalone bot service
│   ├── src/
│   ├── main.py
│   ├── requirements.txt
│   └── docker-compose.yml
├── docker-compose.yml          # Development compose
├── docker-compose.server.yml   # Production compose
└── .env                        # Environment variables
```

## Additional Resources

- **Project Context**: `CONTEXTO_PROYECTO_COMPLETO_20250106.md` - Complete system overview
- **SAP Integration**: `README_SAP_STL.md` - SAP-STL API details
- **Testing Guide**: `GUIA_PRUEBAS_SINCRONIZACION.md` - Sync testing procedures
- **Telegram Migration**: `TELEGRAM_BOT_MIGRATION.md` - Bot setup guide
- **Database Schema**: `tablas_SAP-STL.sql` - Full Firebird DDL

## Next Steps & TODOs

- Fix DialogTitle warnings in React components (add DialogTitle and DialogDescription to all Dialog components)
- Implement manual sync per module from UI
- Add data export functionality
- Create dashboard with sync metrics and charts (Recharts already installed)
- Activate Telegram bot initialization in production
- Configure CI/CD pipeline
