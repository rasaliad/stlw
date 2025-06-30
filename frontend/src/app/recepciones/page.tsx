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
  RefreshCw, 
  Download, 
  Search,
  Truck,
  Calendar,
  Package,
  ChevronDown,
  ChevronUp,
  Building2
} from 'lucide-react'

interface GoodsReceiptLine {
  id: number
  goods_receipt_id: number
  codigo_producto: string | null
  nombre_producto: string | null
  almacen: string | null
  cantidad_umb: number | null
  line_num: number | null
  uom_code: string | null
}

interface GoodsReceipt {
  id: number
  numero_documento: number | null
  numero_busqueda: number | null
  fecha: string | null
  tipo_recepcion: number
  codigo_suplidor: string | null
  nombre_suplidor: string | null
  sync_status: string
  lines: GoodsReceiptLine[]
}

export default function RecepcionesPage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [receipts, setReceipts] = useState<GoodsReceipt[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSyncing, setIsSyncing] = useState(false)
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())
  const [filters, setFilters] = useState({
    codigo_suplidor: '',
    fecha_desde: '',
    fecha_hasta: ''
  })
  const [totalCount, setTotalCount] = useState(0)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [userResponse, receiptsResponse] = await Promise.all([
        api.get<User>('/auth/me'),
        api.get<GoodsReceipt[]>('/goods-receipts/')
      ])
      
      setCurrentUser(userResponse.data)
      setReceipts(receiptsResponse.data)
      setTotalCount(receiptsResponse.data.length)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSync = async () => {
    setIsSyncing(true)
    try {
      const token = localStorage.getItem('token')
      await fetch('http://localhost:8000/api/sap-stl/sync-now', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      await fetchData()
    } catch (error) {
      console.error('Error syncing:', error)
    } finally {
      setIsSyncing(false)
    }
  }

  const handleSearch = async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      if (filters.codigo_suplidor) params.append('codigo_suplidor', filters.codigo_suplidor)
      if (filters.fecha_desde) params.append('fecha_desde', filters.fecha_desde)
      if (filters.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta)
      
      const response = await api.get<GoodsReceipt[]>(`/goods-receipts/?${params.toString()}`)
      setReceipts(response.data)
    } catch (error) {
      console.error('Error searching:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleRowExpanded = (receiptId: number) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(receiptId)) {
      newExpanded.delete(receiptId)
    } else {
      newExpanded.add(receiptId)
    }
    setExpandedRows(newExpanded)
  }

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('es-ES')
  }

  const getTipoRecepcion = (tipo: number): string => {
    const tipos: { [key: number]: string } = {
      1: 'Normal',
      2: 'Urgente',
      3: 'Devolución'
    }
    return tipos[tipo] || `Tipo ${tipo}`
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
            <h2 className="text-3xl font-bold tracking-tight">Recepciones</h2>
            <p className="text-muted-foreground">
              Gestión de recepciones de mercancía del sistema STL
            </p>
          </div>
          
          <div className="flex space-x-2">
            <Button 
              onClick={handleSync} 
              disabled={isSyncing}
              className="btn-cream-primary"
            >
              {isSyncing ? (
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="mr-2 h-4 w-4" />
              )}
              Sincronizar
            </Button>
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
                <Label htmlFor="codigo_suplidor">Código Suplidor</Label>
                <Input
                  id="codigo_suplidor"
                  placeholder="Ej: SUP001"
                  value={filters.codigo_suplidor}
                  onChange={(e) => setFilters({...filters, codigo_suplidor: e.target.value})}
                />
              </div>
              
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
              <CardTitle className="text-sm font-medium">Total Recepciones</CardTitle>
              <Truck className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{totalCount}</div>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Recepciones Hoy</CardTitle>
              <Calendar className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {receipts.filter(r => r.fecha && 
                  new Date(r.fecha).toDateString() === new Date().toDateString()
                ).length}
              </div>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Suplidores Únicos</CardTitle>
              <Building2 className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {new Set(receipts.map(r => r.codigo_suplidor).filter(Boolean)).size}
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
                {receipts.reduce((acc, r) => acc + r.lines.length, 0)}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabla de recepciones */}
        <Card className="card-cream shadow-cream">
          <CardHeader>
            <CardTitle>Lista de Recepciones</CardTitle>
            <CardDescription>
              Mostrando {receipts.length} de {totalCount} recepciones
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12"></TableHead>
                  <TableHead>Nº Documento</TableHead>
                  <TableHead>Suplidor</TableHead>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Estado Sync</TableHead>
                  <TableHead className="text-right">Líneas</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {receipts.map((receipt) => (
                  <>
                    <TableRow 
                      key={receipt.id}
                      className="cursor-pointer hover:bg-accent/50"
                      onClick={() => toggleRowExpanded(receipt.id)}
                    >
                      <TableCell>
                        {expandedRows.has(receipt.id) ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </TableCell>
                      <TableCell className="font-medium">
                        {receipt.numero_documento || '-'}
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{receipt.nombre_suplidor || '-'}</p>
                          <p className="text-sm text-muted-foreground">
                            {receipt.codigo_suplidor || '-'}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>{formatDate(receipt.fecha)}</TableCell>
                      <TableCell>{getTipoRecepcion(receipt.tipo_recepcion)}</TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          receipt.sync_status === 'SYNCED' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {receipt.sync_status}
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        {receipt.lines.length}
                      </TableCell>
                    </TableRow>
                    
                    {expandedRows.has(receipt.id) && (
                      <TableRow>
                        <TableCell colSpan={7} className="p-0">
                          <div className="bg-muted/50 p-4">
                            <h4 className="font-semibold mb-2">Líneas de la recepción</h4>
                            <Table>
                              <TableHeader>
                                <TableRow>
                                  <TableHead>Línea</TableHead>
                                  <TableHead>Código Producto</TableHead>
                                  <TableHead>Nombre Producto</TableHead>
                                  <TableHead>Almacén</TableHead>
                                  <TableHead className="text-right">Cantidad</TableHead>
                                  <TableHead>UOM</TableHead>
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {receipt.lines.map((line) => (
                                  <TableRow key={line.id}>
                                    <TableCell>{line.line_num || '-'}</TableCell>
                                    <TableCell>{line.codigo_producto || '-'}</TableCell>
                                    <TableCell>{line.nombre_producto || '-'}</TableCell>
                                    <TableCell>{line.almacen || '-'}</TableCell>
                                    <TableCell className="text-right">
                                      {line.cantidad_umb ? Number(line.cantidad_umb).toFixed(2) : '-'}
                                    </TableCell>
                                    <TableCell>{line.uom_code || '-'}</TableCell>
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
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}