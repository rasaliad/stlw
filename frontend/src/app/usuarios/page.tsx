'use client'

import { useState, useEffect } from 'react'
import { AppLayout } from '@/components/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { UserTable } from '@/components/user-table'
import { api } from '@/lib/api'
import { User } from '@/types/user'

export default function UsuariosPage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [userResponse, usersResponse] = await Promise.all([
        api.get<User>('/auth/me'),
        api.get<User[]>('/users/')
      ])
      
      setCurrentUser(userResponse.data)
      setUsers(usersResponse.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setIsLoading(false)
    }
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
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Usuarios</h2>
          <p className="text-muted-foreground">
            Gestión de usuarios del sistema STL
          </p>
        </div>

        <Card className="card-cream shadow-cream">
          <CardHeader>
            <CardTitle>Lista de Usuarios</CardTitle>
            <CardDescription>
              Administra los usuarios y sus permisos en el sistema
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