'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { Sidebar, MobileSidebar } from '@/components/sidebar'
import { LogOut } from 'lucide-react'

interface AppLayoutProps {
  children: React.ReactNode
  currentUser?: {
    username: string
  }
}

export function AppLayout({ children, currentUser }: AppLayoutProps) {
  const router = useRouter()

  const handleLogout = () => {
    localStorage.removeItem('token')
    router.push('/')
  }

  return (
    <div className="flex min-h-screen">
      {/* Sidebar para desktop */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div className="sidebar-cream h-full overflow-y-auto">
          <Sidebar />
        </div>
      </div>

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col md:ml-64">
        {/* Header */}
        <header className="header-cream sticky top-0 z-40">
          <div className="flex h-16 items-center px-4 md:px-6">
            <div className="flex items-center space-x-4">
              {/* Botón de menú móvil */}
              <MobileSidebar />
              <h1 className="text-xl font-semibold text-foreground md:hidden">STL</h1>
            </div>
            
            <div className="ml-auto flex items-center space-x-4">
              {currentUser && (
                <span className="text-sm text-muted-foreground">
                  Bienvenido, {currentUser.username}
                </span>
              )}
              <ThemeToggle />
              <Button variant="ghost" size="icon" onClick={handleLogout}>
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </header>

        {/* Contenido de la página */}
        <main className="flex-1 p-4 md:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}