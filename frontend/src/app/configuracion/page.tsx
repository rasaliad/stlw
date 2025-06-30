'use client'

import { useState, useEffect } from 'react'
import { AppLayout } from '@/components/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { api } from '@/lib/api'
import { User } from '@/types/user'
import { Save, RefreshCw } from 'lucide-react'

interface SyncConfig {
  id: number
  entity_type: string
  sync_enabled: string
  sync_interval_minutes: number
  batch_size: number
  max_retries: number
  api_endpoint: string
  last_sync_at: string | null
  next_sync_at: string | null
  created_at: string
  updated_at: string
}

export default function ConfiguracionPage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [configs, setConfigs] = useState<SyncConfig[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [userResponse, configsResponse] = await Promise.all([
        api.get<User>('/auth/me'),
        api.get<SyncConfig[]>('/sync-config/')
      ])
      
      setCurrentUser(userResponse.data)
      setConfigs(configsResponse.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleConfigUpdate = async (entityType: string, field: string, value: any) => {
    setIsSaving(entityType)
    
    try {
      const updateData: any = {}
      updateData[field] = value
      
      const response = await api.put<SyncConfig>(`/sync-config/${entityType}`, updateData)
      
      setConfigs(configs.map(config => 
        config.entity_type === entityType ? response.data : config
      ))
    } catch (error) {
      console.error('Error updating config:', error)
    } finally {
      setIsSaving(null)
    }
  }

  const getEntityName = (entityType: string): string => {
    const names: { [key: string]: string } = {
      'ITEMS': 'Productos',
      'DISPATCHES': 'Despachos',
      'GOODS_RECEIPTS': 'Recepciones',
      'PROCUREMENT_ORDERS': 'Órdenes de Compra'
    }
    return names[entityType] || entityType
  }

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'Nunca'
    return new Date(dateString).toLocaleString('es-ES')
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

  if (currentUser?.role !== 'ADMINISTRADOR') {
    return (
      <AppLayout currentUser={currentUser || undefined}>
        <div className="flex items-center justify-center min-h-96">
          <Card className="card-cream">
            <CardHeader>
              <CardTitle>Acceso Denegado</CardTitle>
              <CardDescription>
                Solo los administradores pueden acceder a la configuración
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout currentUser={currentUser || undefined}>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Configuración de Sincronización</h2>
          <p className="text-muted-foreground">
            Administra los tiempos y parámetros de sincronización con SAP STL
          </p>
        </div>

        {configs.map((config) => (
          <Card key={config.entity_type} className="card-cream shadow-cream">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{getEntityName(config.entity_type)}</span>
                <div className="flex items-center space-x-2">
                  <Label htmlFor={`${config.entity_type}-enabled`}>Activo</Label>
                  <Switch
                    id={`${config.entity_type}-enabled`}
                    checked={config.sync_enabled === 'Y'}
                    onCheckedChange={(checked) => 
                      handleConfigUpdate(config.entity_type, 'sync_enabled', checked ? 'Y' : 'N')
                    }
                    disabled={isSaving === config.entity_type}
                  />
                </div>
              </CardTitle>
              <CardDescription>
                Endpoint: {config.api_endpoint}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor={`${config.entity_type}-interval`}>
                    Intervalo (minutos)
                  </Label>
                  <div className="flex space-x-2">
                    <Input
                      id={`${config.entity_type}-interval`}
                      type="number"
                      value={config.sync_interval_minutes}
                      onChange={(e) => 
                        handleConfigUpdate(config.entity_type, 'sync_interval_minutes', parseInt(e.target.value))
                      }
                      disabled={isSaving === config.entity_type}
                      min="1"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor={`${config.entity_type}-batch`}>
                    Tamaño de lote
                  </Label>
                  <Input
                    id={`${config.entity_type}-batch`}
                    type="number"
                    value={config.batch_size}
                    onChange={(e) => 
                      handleConfigUpdate(config.entity_type, 'batch_size', parseInt(e.target.value))
                    }
                    disabled={isSaving === config.entity_type}
                    min="1"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor={`${config.entity_type}-retries`}>
                    Reintentos máximos
                  </Label>
                  <Input
                    id={`${config.entity_type}-retries`}
                    type="number"
                    value={config.max_retries}
                    onChange={(e) => 
                      handleConfigUpdate(config.entity_type, 'max_retries', parseInt(e.target.value))
                    }
                    disabled={isSaving === config.entity_type}
                    min="0"
                  />
                </div>
              </div>
              
              <div className="flex items-center justify-between pt-4 border-t">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">
                    Última sincronización: {formatDate(config.last_sync_at)}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Próxima sincronización: {formatDate(config.next_sync_at)}
                  </p>
                </div>
                
                {isSaving === config.entity_type && (
                  <div className="flex items-center space-x-2 text-primary">
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Guardando...</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </AppLayout>
  )
}