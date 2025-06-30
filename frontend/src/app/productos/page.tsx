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
  Package,
  Calendar,
  Tag,
  Archive
} from 'lucide-react'

interface Product {
  id: number
  codigo_producto: string | null
  descripcion_producto: string | null
  codigo_producto_erp: string | null
  codigo_familia: number | null
  nombre_familia: string | null
  dias_vencimiento: number | null
  codigo_umb: string | null
  descripcion_umb: string | null
  codigo_forma_embalaje: string | null
  nombre_forma_embalaje: string | null
  created_at: string | null
  last_sync_at: string | null
}

export default function ProductosPage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSyncing, setIsSyncing] = useState(false)
  const [filters, setFilters] = useState({
    search: '',
    codigo_familia: ''
  })
  const [totalCount, setTotalCount] = useState(0)
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 50,
    total: 0
  })

  useEffect(() => {
    fetchData()
  }, [pagination.page])

  const fetchData = async () => {
    try {
      const [userResponse, productsResponse] = await Promise.all([
        api.get<User>('/auth/me'),
        api.get<{items: Product[], total: number}>(`/items/?skip=${(pagination.page - 1) * pagination.limit}&limit=${pagination.limit}`)
      ])
      
      setCurrentUser(userResponse.data)
      setProducts(productsResponse.data.items)
      setTotalCount(productsResponse.data.total)
      setPagination(prev => ({ ...prev, total: productsResponse.data.total }))
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
      if (filters.search) params.append('search', filters.search)
      if (filters.codigo_familia) params.append('codigo_familia', filters.codigo_familia)
      params.append('skip', '0')
      params.append('limit', pagination.limit.toString())
      
      const response = await api.get<{items: Product[], total: number}>(`/items/?${params.toString()}`)
      setProducts(response.data.items)
      setTotalCount(response.data.total)
      setPagination(prev => ({ ...prev, page: 1, total: response.data.total }))
    } catch (error) {
      console.error('Error searching:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handlePageChange = (newPage: number) => {
    setPagination(prev => ({ ...prev, page: newPage }))
  }

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('es-ES')
  }

  const totalPages = Math.ceil(pagination.total / pagination.limit)

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
            <h2 className="text-3xl font-bold tracking-tight">Productos</h2>
            <p className="text-muted-foreground">
              Catálogo de productos del sistema STL
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
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="search">Buscar Producto</Label>
                <Input
                  id="search"
                  placeholder="Código o descripción..."
                  value={filters.search}
                  onChange={(e) => setFilters({...filters, search: e.target.value})}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="codigo_familia">Código Familia</Label>
                <Input
                  id="codigo_familia"
                  placeholder="Ej: 122"
                  value={filters.codigo_familia}
                  onChange={(e) => setFilters({...filters, codigo_familia: e.target.value})}
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
              <CardTitle className="text-sm font-medium">Total Productos</CardTitle>
              <Package className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{totalCount}</div>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Familias Únicas</CardTitle>
              <Tag className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {new Set(products.map(p => p.codigo_familia).filter(Boolean)).size}
              </div>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Con Vencimiento</CardTitle>
              <Calendar className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {products.filter(p => p.dias_vencimiento && p.dias_vencimiento > 0).length}
              </div>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tipos Embalaje</CardTitle>
              <Archive className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {new Set(products.map(p => p.codigo_forma_embalaje).filter(Boolean)).size}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabla de productos */}
        <Card className="card-cream shadow-cream">
          <CardHeader>
            <CardTitle>Catálogo de Productos</CardTitle>
            <CardDescription>
              Mostrando {products.length} de {totalCount} productos (Página {pagination.page} de {totalPages})
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Código</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Familia</TableHead>
                  <TableHead>UMB</TableHead>
                  <TableHead>Embalaje</TableHead>
                  <TableHead>Venc. (días)</TableHead>
                  <TableHead>Última Sync</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {products.map((product) => (
                  <TableRow key={product.id}>
                    <TableCell className="font-medium">
                      {product.codigo_producto || '-'}
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{product.descripcion_producto || '-'}</p>
                        {product.codigo_producto_erp && (
                          <p className="text-sm text-muted-foreground">
                            ERP: {product.codigo_producto_erp}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{product.codigo_familia || '-'}</p>
                        {product.nombre_familia && (
                          <p className="text-sm text-muted-foreground">
                            {product.nombre_familia}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{product.codigo_umb || '-'}</p>
                        {product.descripcion_umb && (
                          <p className="text-sm text-muted-foreground">
                            {product.descripcion_umb}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{product.codigo_forma_embalaje || '-'}</p>
                        {product.nombre_forma_embalaje && (
                          <p className="text-sm text-muted-foreground">
                            {product.nombre_forma_embalaje}
                          </p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      {product.dias_vencimiento || '-'}
                    </TableCell>
                    <TableCell>{formatDate(product.last_sync_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            
            {/* Paginación */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between space-x-2 py-4">
                <div className="text-sm text-muted-foreground">
                  Página {pagination.page} de {totalPages}
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={pagination.page <= 1}
                  >
                    Anterior
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={pagination.page >= totalPages}
                  >
                    Siguiente
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}