'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { 
  LayoutDashboard, 
  Package, 
  Truck, 
  PackageCheck, 
  Users, 
  Settings, 
  Menu,
  RefreshCw,
  Download,
  ChevronDown,
  ChevronRight,
  Database,
  Building2
} from 'lucide-react'

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname()
  const [sapExpanded, setSapExpanded] = useState(true)
  const [stlExpanded, setStlExpanded] = useState(true)

  return (
    <div className={cn('pb-12 min-h-screen', className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <div className="space-y-1">
            <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight text-primary">
              Sistema STL
            </h2>
            
            {/* Dashboard */}
            <div className="space-y-1">
              <Link
                href="/dashboard"
                className={cn(
                  'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground list-item-cream',
                  pathname === '/dashboard'
                    ? 'bg-primary text-primary-foreground shadow-sm' 
                    : 'text-muted-foreground'
                )}
              >
                <LayoutDashboard className="mr-3 h-4 w-4" />
                Dashboard
              </Link>
            </div>

            {/* Grupo Desde SAP */}
            <div className="space-y-1 mt-4">
              <button
                onClick={() => setSapExpanded(!sapExpanded)}
                className="flex items-center w-full rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-all"
              >
                <Database className="mr-2 h-4 w-4" />
                <span className="flex-1 text-left">Desde SAP</span>
                {sapExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </button>
              
              {sapExpanded && (
                <div className="ml-4 space-y-1">
                  <Link
                    href="/productos"
                    className={cn(
                      'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground list-item-cream',
                      pathname === '/productos'
                        ? 'bg-primary text-primary-foreground shadow-sm' 
                        : 'text-muted-foreground'
                    )}
                  >
                    <Package className="mr-3 h-4 w-4" />
                    Productos
                  </Link>
                  
                  <Link
                    href="/despachos"
                    className={cn(
                      'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground list-item-cream',
                      pathname === '/despachos'
                        ? 'bg-primary text-primary-foreground shadow-sm' 
                        : 'text-muted-foreground'
                    )}
                  >
                    <Truck className="mr-3 h-4 w-4" />
                    Despachos
                  </Link>
                  
                  <Link
                    href="/recepciones"
                    className={cn(
                      'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground list-item-cream',
                      pathname === '/recepciones'
                        ? 'bg-primary text-primary-foreground shadow-sm' 
                        : 'text-muted-foreground'
                    )}
                  >
                    <PackageCheck className="mr-3 h-4 w-4" />
                    Recepciones
                  </Link>
                </div>
              )}
            </div>

            {/* Grupo En STL */}
            <div className="space-y-1 mt-4">
              <button
                onClick={() => setStlExpanded(!stlExpanded)}
                className="flex items-center w-full rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-all"
              >
                <Building2 className="mr-2 h-4 w-4" />
                <span className="flex-1 text-left">En STL</span>
                {stlExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </button>
              
              {stlExpanded && (
                <div className="ml-4 space-y-1">
                  <Link
                    href="/stl/productos"
                    className={cn(
                      'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground list-item-cream',
                      pathname === '/stl/productos'
                        ? 'bg-primary text-primary-foreground shadow-sm' 
                        : 'text-muted-foreground'
                    )}
                  >
                    <Package className="mr-3 h-4 w-4" />
                    Productos
                  </Link>
                  
                  <Link
                    href="/stl/despachos"
                    className={cn(
                      'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground list-item-cream',
                      pathname === '/stl/despachos'
                        ? 'bg-primary text-primary-foreground shadow-sm' 
                        : 'text-muted-foreground'
                    )}
                  >
                    <Truck className="mr-3 h-4 w-4" />
                    Despachos
                  </Link>
                  
                  <Link
                    href="/stl/recepciones"
                    className={cn(
                      'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground list-item-cream',
                      pathname === '/stl/recepciones'
                        ? 'bg-primary text-primary-foreground shadow-sm' 
                        : 'text-muted-foreground'
                    )}
                  >
                    <PackageCheck className="mr-3 h-4 w-4" />
                    Recepciones
                  </Link>
                </div>
              )}
            </div>

            {/* Usuarios y Configuración fuera de grupos */}
            <div className="space-y-1 mt-4">
              <Link
                href="/usuarios"
                className={cn(
                  'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground list-item-cream',
                  pathname === '/usuarios'
                    ? 'bg-primary text-primary-foreground shadow-sm' 
                    : 'text-muted-foreground'
                )}
              >
                <Users className="mr-3 h-4 w-4" />
                Usuarios
              </Link>
              
              <Link
                href="/configuracion"
                className={cn(
                  'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground list-item-cream',
                  pathname === '/configuracion'
                    ? 'bg-primary text-primary-foreground shadow-sm' 
                    : 'text-muted-foreground'
                )}
              >
                <Settings className="mr-3 h-4 w-4" />
                Configuración
              </Link>
            </div>
          </div>
        </div>

        {/* Acciones rápidas */}
        <div className="px-3 py-2">
          <h3 className="mb-2 px-4 text-sm font-semibold tracking-tight text-muted-foreground">
            Acciones Rápidas
          </h3>
          <div className="space-y-1">
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-muted-foreground hover:text-foreground"
            >
              <RefreshCw className="mr-3 h-4 w-4" />
              Sincronizar Todo
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-muted-foreground hover:text-foreground"
            >
              <Download className="mr-3 h-4 w-4" />
              Exportar Datos
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export function MobileSidebar() {
  const [open, setOpen] = useState(false)

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
        >
          <Menu className="h-5 w-5" />
          <span className="sr-only">Abrir menú</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-64 p-0">
        <div className="sidebar-cream">
          <Sidebar />
        </div>
      </SheetContent>
    </Sheet>
  )
}