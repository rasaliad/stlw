'use client'

import { useState, useEffect } from 'react'
import { AppLayout } from '@/components/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api'
import { User } from '@/types/user'
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { 
  Download, 
  Search,
  Truck,
  Calendar,
  Package,
  ChevronDown,
  ChevronUp,
  Building2
} from 'lucide-react'

interface PedidoDetalle {
  id: number
  id_pedido: number
  codigo_producto: string | null
  nombre_producto: string | null
  cantidad_pedida: number | null
  cantidad_despachada: number | null
  precio_unitario: number | null
  total_linea: number | null
}

interface Pedido {
  id: number
  numero_pedido: string | null
  fecha_pedido: string | null
  fecha_despacho: string | null
  codigo_cliente: string | null
  nombre_cliente: string | null
  estado: string | null
  total_pedido: number | null
  observaciones: string | null
  detalles: PedidoDetalle[]
}

export default function STLDespachosPage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [pedidos, setPedidos] = useState<Pedido[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())
  const [filters, setFilters] = useState({
    fecha_desde: (() => {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    })(),
    fecha_hasta: (() => {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    })(),
    codigo_cliente: ''
  })
  const [totalCount, setTotalCount] = useState(0)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [userResponse] = await Promise.all([
        api.get<User>('/auth/me')
      ])
      
      setCurrentUser(userResponse.data)
      await handleSearch()
      
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      if (filters.fecha_desde) params.append('fecha_desde', filters.fecha_desde)
      if (filters.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta)
      if (filters.codigo_cliente) params.append('codigo_cliente', filters.codigo_cliente)
      
      const response = await api.get<Pedido[]>(`/stl/pedidos/?${params.toString()}`)
      setPedidos(response.data)
      setTotalCount(response.data.length)
    } catch (error) {
      console.error('Error searching pedidos:', error)
      setPedidos([])
      setTotalCount(0)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleRowExpanded = (pedidoId: number) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(pedidoId)) {
      newExpanded.delete(pedidoId)
    } else {
      newExpanded.add(pedidoId)
    }
    setExpandedRows(newExpanded)
  }

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('es-ES')
  }

  const formatNumber = (num: number | null): string => {
    if (!num && num !== 0) return '-'
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(num)
  }

  if (isLoading) {
    return (
      <AppLayout currentUser={currentUser || undefined}>
        <div className="flex items-center justify-center min-h-96">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout currentUser={currentUser || undefined}>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">STL Despachos</h2>
            <p className="text-muted-foreground">
              Gestión de despachos del almacén STL
            </p>
          </div>
          
          <div className="flex space-x-2">
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Exportar
            </Button>
          </div>
        </div>

        {/* Filtros */}
        <Card className="card-cream">
          <CardHeader>
            <CardTitle>Filtros de búsqueda</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor="fecha_desde">Fecha Desde</Label>
                <Input
                  id="fecha_desde"
                  type="date"
                  value={filters.fecha_desde}
                  onChange={(e) => setFilters({...filters, fecha_desde: e.target.value})}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="fecha_hasta">Fecha Hasta</Label>
                <Input
                  id="fecha_hasta"
                  type="date"
                  value={filters.fecha_hasta}
                  onChange={(e) => setFilters({...filters, fecha_hasta: e.target.value})}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="codigo_cliente">Código Cliente</Label>
                <Input
                  id="codigo_cliente"
                  placeholder="Ej: CLI001"
                  value={filters.codigo_cliente}
                  onChange={(e) => setFilters({...filters, codigo_cliente: e.target.value})}
                />
              </div>
              
              <div className="flex items-end">
                <Button onClick={handleSearch} className="w-full">
                  <Search className="mr-2 h-4 w-4" />
                  Buscar
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Estadísticas */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Despachos</CardTitle>
              <Building2 className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{totalCount}</div>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Despachos Hoy</CardTitle>
              <Calendar className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {pedidos.filter(p => p.fecha_despacho && 
                  new Date(p.fecha_despacho).toDateString() === new Date().toDateString()
                ).length}
              </div>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Clientes Únicos</CardTitle>
              <Truck className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {new Set(pedidos.map(p => p.codigo_cliente).filter(Boolean)).size}
              </div>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Productos Total</CardTitle>
              <Package className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {pedidos.reduce((acc, p) => acc + (p.detalles?.length || 0), 0)}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabla de pedidos STL */}
        <Card className="card-cream shadow-cream">
          <CardHeader>
            <CardTitle>Lista de Despachos STL</CardTitle>
            <CardDescription>
              Mostrando {pedidos.length} despachos para el período seleccionado
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12"></TableHead>
                  <TableHead>Nº Pedido</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Fecha Pedido</TableHead>
                  <TableHead>Fecha Despacho</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Líneas</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pedidos.map((pedido) => (
                  <>
                    <TableRow 
                      key={pedido.id}
                      className="cursor-pointer hover:bg-accent/50"
                      onClick={() => toggleRowExpanded(pedido.id)}
                    >
                      <TableCell>
                        {expandedRows.has(pedido.id) ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </TableCell>
                      <TableCell className="font-medium">
                        {pedido.numero_pedido || '-'}
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{pedido.nombre_cliente || '-'}</p>
                          <p className="text-sm text-muted-foreground">
                            {pedido.codigo_cliente || '-'}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>{formatDate(pedido.fecha_pedido)}</TableCell>
                      <TableCell>{formatDate(pedido.fecha_despacho)}</TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          pedido.estado?.trim() === 'DESPACHADO' 
                            ? 'bg-green-100 text-green-800' 
                            : pedido.estado?.trim() === 'PENDIENTE'
                            ? 'bg-yellow-100 text-yellow-800'
                            : pedido.estado?.trim() === 'DISPONIBLE'
                            ? 'bg-blue-100 text-blue-800'
                            : pedido.estado?.trim() === 'ERP'
                            ? 'bg-purple-100 text-purple-800'
                            : pedido.estado?.trim() === 'PICKING'
                            ? 'bg-orange-100 text-orange-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {pedido.estado || 'N/A'}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        {pedido.detalles?.length || 0}
                      </TableCell>
                    </TableRow>
                    
                    {expandedRows.has(pedido.id) && (
                      <TableRow>
                        <TableCell colSpan={7} className="p-0">
                          <div className="bg-muted/50 p-4">
                            <h4 className="font-semibold mb-2">Detalles del despacho</h4>
                            <Table>
                              <TableHeader>
                                <TableRow>
                                  <TableHead>Posición</TableHead>
                                  <TableHead>Código Producto</TableHead>
                                  <TableHead>Nombre Producto</TableHead>
                                  <TableHead className="text-right">Cant. Pedida</TableHead>
                                  <TableHead className="text-right">Cant. Despachada</TableHead>
                                  <TableHead className="text-right">Diferencia</TableHead>
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {pedido.detalles?.map((detalle, index) => (
                                  <TableRow key={detalle.id}>
                                    <TableCell>{index + 1}</TableCell>
                                    <TableCell>{detalle.codigo_producto || '-'}</TableCell>
                                    <TableCell>{detalle.nombre_producto || '-'}</TableCell>
                                    <TableCell className="text-right">
                                      {formatNumber(detalle.cantidad_pedida)}
                                    </TableCell>
                                    <TableCell className="text-right">
                                      {formatNumber(detalle.cantidad_despachada)}
                                    </TableCell>
                                    <TableCell className="text-right">
                                      {formatNumber(detalle.total_linea)}
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </>
                ))}
              </TableBody>
            </Table>
            
            {pedidos.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No se encontraron despachos para los filtros seleccionados
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}