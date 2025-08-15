'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

interface SyncResult {
  success: boolean
  message: string
  data?: {
    tipoDespacho: number
    docNum: number
    numeroDespacho: number
    numeroBusqueda: number
    codigoCliente: string
    nombreCliente: string
    action: string
    stats: {
      inserted: number
      updated: number
      skipped: number
      lines_inserted: number
      lines_updated: number
      lines_skipped: number
    }
    processing_time: number
  }
}

const DISPATCH_TYPES = [
  { value: 201, label: "Despacho Normal (201)" },
  { value: 202, label: "Despacho Urgente (202)" },
  { value: 203, label: "Despacho Express (203)" },
  { value: 204, label: "Transferencia (204)" },
]

export default function SyncManualDispatch() {
  const [tipoDespacho, setTipoDespacho] = useState<string>("")
  const [docNum, setDocNum] = useState<string>("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<SyncResult | null>(null)

  const handleSync = async () => {
    if (!tipoDespacho || !docNum) {
      setResult({
        success: false,
        message: "Por favor complete todos los campos"
      })
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const token = localStorage.getItem('token')
      
      const response = await fetch('/api/v1/sap/sync/single-dispatch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          tipoDespacho: parseInt(tipoDespacho),
          docNum: parseInt(docNum)
        })
      })

      const data = await response.json()

      if (response.ok) {
        setResult(data)
      } else {
        setResult({
          success: false,
          message: data.detail || 'Error en la sincronización'
        })
      }
    } catch (error) {
      setResult({
        success: false,
        message: `Error de conexión: ${error}`
      })
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setTipoDespacho("")
    setDocNum("")
    setResult(null)
  }

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Sincronización Manual de Pedidos
        </CardTitle>
        <CardDescription>
          Sincronizar un pedido específico desde SAP usando Tipo de Despacho + Número de Documento
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="tipoDespacho">Tipo de Despacho</Label>
            <Select value={tipoDespacho} onValueChange={setTipoDespacho}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar tipo..." />
              </SelectTrigger>
              <SelectContent>
                {DISPATCH_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value.toString()}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="docNum">Número de Documento</Label>
            <Input
              id="docNum"
              type="number"
              placeholder="Ej: 12345"
              value={docNum}
              onChange={(e) => setDocNum(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        <div className="flex gap-2">
          <Button 
            onClick={handleSync}
            disabled={loading || !tipoDespacho || !docNum}
            className="flex-1"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sincronizando...
              </>
            ) : (
              'Sincronizar Pedido'
            )}
          </Button>
          
          <Button 
            variant="outline" 
            onClick={resetForm}
            disabled={loading}
          >
            Limpiar
          </Button>
        </div>

        {/* Resultado */}
        {result && (
          <div className={`p-4 rounded-lg border ${
            result.success 
              ? 'bg-green-50 border-green-200 text-green-800' 
              : 'bg-red-50 border-red-200 text-red-800'
          }`}>
            <div className="flex items-center gap-2 font-medium mb-2">
              {result.success ? (
                <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
              {result.success ? 'Sincronización Exitosa' : 'Error en Sincronización'}
            </div>
            
            <p className="text-sm mb-3">{result.message}</p>
            
            {result.success && result.data && (
              <div className="bg-white bg-opacity-50 p-3 rounded border text-xs space-y-1">
                <div className="grid grid-cols-2 gap-2">
                  <div><strong>Tipo Despacho:</strong> {result.data.tipoDespacho}</div>
                  <div><strong>Doc Num:</strong> {result.data.docNum}</div>
                  <div><strong>Número Despacho:</strong> {result.data.numeroDespacho}</div>
                  <div><strong>Número Búsqueda:</strong> {result.data.numeroBusqueda}</div>
                  <div><strong>Cliente:</strong> {result.data.codigoCliente}</div>
                  <div><strong>Nombre:</strong> {result.data.nombreCliente}</div>
                </div>
                
                <div className="mt-2 pt-2 border-t">
                  <strong>Acción:</strong> {result.data.action} | 
                  <strong> Tiempo:</strong> {result.data.processing_time.toFixed(2)}s | 
                  <strong> Líneas:</strong> +{result.data.stats.lines_inserted} ~{result.data.stats.lines_updated}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded">
          <strong>Nota:</strong> Esta función sincroniza un pedido específico desde SAP usando el endpoint 
          <code className="bg-white px-1 rounded">GET /Transaction/Orders/{'{tipoDespacho}'}/{'{docNum}'}</code>. 
          El pedido se insertará o actualizará en las tablas STL_DISPATCHES y STL_DISPATCH_LINES.
        </div>
      </CardContent>
    </Card>
  )
}