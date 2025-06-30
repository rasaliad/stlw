'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api'
import { User, UserCreate, UserUpdate } from '@/types/user'
import { Plus, Search, Edit, Trash2, Mail, User as UserIcon } from 'lucide-react'

interface UserTableProps {
  users: User[]
  onUsersChange: (users: User[]) => void
}

export function UserTable({ users, onUsersChange }: UserTableProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [newUser, setNewUser] = useState<UserCreate>({
    username: '',
    email: '',
    password: '',
    role: 'OPERADOR'
  })

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleCreateUser = async () => {
    if (!newUser.username || !newUser.email || !newUser.password) {
      alert('Por favor complete todos los campos')
      return
    }

    try {
      const response = await api.post<User>('/users/', newUser)
      onUsersChange([...users, response.data])
      setNewUser({ username: '', email: '', password: '', role: 'OPERADOR' })
      setIsCreating(false)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error creando usuario')
    }
  }

  const handleEditUser = (user: User) => {
    setEditingUser(user)
  }

  const handleUpdateUser = async () => {
    if (!editingUser) return

    try {
      const updateData: UserUpdate = {
        username: editingUser.username,
        email: editingUser.email,
        is_active: editingUser.is_active,
        role: editingUser.role
      }
      
      const response = await api.put<User>(`/users/${editingUser.id}`, updateData)
      onUsersChange(users.map(u => u.id === editingUser.id ? response.data : u))
      setEditingUser(null)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error actualizando usuario')
    }
  }

  const handleCancelEdit = () => {
    setEditingUser(null)
  }

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('¿Estás seguro de eliminar este usuario?')) return

    try {
      await api.delete(`/users/${userId}`)
      onUsersChange(users.filter(u => u.id !== userId))
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error eliminando usuario')
    }
  }

  const toggleUserStatus = async (user: User) => {
    try {
      const response = await api.put<User>(`/users/${user.id}`, {
        is_active: !user.is_active
      })
      onUsersChange(users.map(u => u.id === user.id ? response.data : u))
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error actualizando usuario')
    }
  }

  return (
    <div className="space-y-4">
      {/* Header Actions */}
      <div className="flex justify-between items-center">
        <div className="relative w-64">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar usuarios..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8"
          />
        </div>
        
        <Button onClick={() => setIsCreating(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Usuario
        </Button>
      </div>

      {/* Create User Form */}
      {isCreating && (
        <div className="border rounded-lg p-4 bg-muted/50">
          <h3 className="text-lg font-semibold mb-4">Crear Nuevo Usuario</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              placeholder="Usuario"
              value={newUser.username}
              onChange={(e) => setNewUser(prev => ({ ...prev, username: e.target.value }))}
            />
            <Input
              placeholder="Email"
              type="email"
              value={newUser.email}
              onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
            />
            <Input
              placeholder="Contraseña"
              type="password"
              value={newUser.password}
              onChange={(e) => setNewUser(prev => ({ ...prev, password: e.target.value }))}
            />
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              value={newUser.role || 'OPERADOR'}
              onChange={(e) => setNewUser(prev => ({ ...prev, role: e.target.value }))}
            >
              <option value="OPERADOR">Operador</option>
              <option value="ADMINISTRADOR">Administrador</option>
            </select>
          </div>
          <div className="flex gap-2 mt-4">
            <Button onClick={handleCreateUser}>Crear</Button>
            <Button variant="outline" onClick={() => setIsCreating(false)}>
              Cancelar
            </Button>
          </div>
        </div>
      )}

      {/* Edit User Form */}
      {editingUser && (
        <div className="border rounded-lg p-4 bg-muted/50">
          <h3 className="text-lg font-semibold mb-4">Editar Usuario</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              placeholder="Usuario"
              value={editingUser.username}
              onChange={(e) => setEditingUser(prev => prev ? { ...prev, username: e.target.value } : null)}
            />
            <Input
              placeholder="Email"
              type="email"
              value={editingUser.email}
              onChange={(e) => setEditingUser(prev => prev ? { ...prev, email: e.target.value } : null)}
            />
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              value={editingUser.is_active ? 'true' : 'false'}
              onChange={(e) => setEditingUser(prev => prev ? { ...prev, is_active: e.target.value === 'true' } : null)}
            >
              <option value="true">Activo</option>
              <option value="false">Inactivo</option>
            </select>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              value={editingUser.role || 'OPERADOR'}
              onChange={(e) => setEditingUser(prev => prev ? { ...prev, role: e.target.value } : null)}
            >
              <option value="OPERADOR">Operador</option>
              <option value="ADMINISTRADOR">Administrador</option>
            </select>
          </div>
          <div className="flex gap-2 mt-4">
            <Button onClick={handleUpdateUser}>Actualizar</Button>
            <Button variant="outline" onClick={handleCancelEdit}>
              Cancelar
            </Button>
          </div>
        </div>
      )}

      {/* Users Table */}
      <div className="border rounded-lg">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="text-left p-4 font-medium">Usuario</th>
                <th className="text-left p-4 font-medium">Email</th>
                <th className="text-left p-4 font-medium">Rol</th>
                <th className="text-left p-4 font-medium">Estado</th>
                <th className="text-left p-4 font-medium">Fecha Creación</th>
                <th className="text-left p-4 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id} className="border-b hover:bg-muted/25">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <UserIcon className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{user.username}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      {user.email}
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      user.role === 'ADMINISTRADOR' 
                        ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                        : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                    }`}>
                      {user.role || 'OPERADOR'}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      user.is_active 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="p-4 text-sm text-muted-foreground">
                    {user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                  </td>
                  <td className="p-4">
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEditUser(user)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleUserStatus(user)}
                      >
                        {user.is_active ? 'Desactivar' : 'Activar'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredUsers.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            No se encontraron usuarios
          </div>
        )}
      </div>
    </div>
  )
}