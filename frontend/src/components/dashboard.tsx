'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { UserTable } from '@/components/user-table'
import { AppLayout } from '@/components/app-layout'
import { api } from '@/lib/api'
import { User } from '@/types/user'
import { Users, BarChart3, Settings, Package, Truck, PackageCheck } from 'lucide-react'

export default function Dashboard() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const response = await api.get<User>('/auth/me')
        setCurrentUser(response.data)
      } catch (error) {
        console.error('Error fetching current user:', error)
      }
    }

    const fetchUsers = async () => {
      try {
        const response = await api.get<User[]>('/users/')
        setUsers(response.data)
      } catch (error) {
        console.error('Error fetching users:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchCurrentUser()
    fetchUsers()
  }, [])

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
        {/* Stats Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Usuarios
              </CardTitle>
              <Users className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{users.length}</div>
              <p className="text-xs text-muted-foreground">
                Usuarios registrados en el sistema
              </p>
            </CardContent>
          </Card>
          
          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Usuarios Activos
              </CardTitle>
              <Users className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {users.filter(u => u.is_active).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Usuarios activos
              </p>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Base de Datos
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-600">Conectado</div>
              <p className="text-xs text-muted-foreground">
                Firebird 2.5
              </p>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Sistema
              </CardTitle>
              <Settings className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-600">Online</div>
              <p className="text-xs text-muted-foreground">
                Todos los servicios funcionando
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Estadísticas del Sistema */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Productos
              </CardTitle>
              <Package className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">0</div>
              <p className="text-xs text-muted-foreground">
                Productos sincronizados
              </p>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Despachos Pendientes
              </CardTitle>
              <Truck className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">0</div>
              <p className="text-xs text-muted-foreground">
                Despachos por procesar
              </p>
            </CardContent>
          </Card>

          <Card className="card-cream-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Recepciones del Día
              </CardTitle>
              <PackageCheck className="h-4 w-4 text-primary/70" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">0</div>
              <p className="text-xs text-muted-foreground">
                Recepciones registradas hoy
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Users Table */}
        <Card className="card-cream shadow-cream">
          <CardHeader>
            <CardTitle className="text-foreground">Gestión de Usuarios</CardTitle>
            <CardDescription>
              Administra los usuarios del sistema STL
            </CardDescription>
          </CardHeader>
          <CardContent>
            <UserTable users={users} onUsersChange={setUsers} />
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}