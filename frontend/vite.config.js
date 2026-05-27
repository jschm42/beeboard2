import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'
import fs from 'node:fs'
import path from 'node:path'

const versionFile = path.resolve(process.cwd(), '..', 'VERSION')
let appVersion = '2.1.0'
try {
  const fileVersion = fs.readFileSync(versionFile, 'utf-8').trim()
  if (fileVersion) {
    appVersion = fileVersion
  }
} catch {
  // Fallback keeps local dev/build working when VERSION is missing.
}

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file from the repository root (..)
  const env = loadEnv(mode, path.resolve(process.cwd(), '..'), '')
  
  const frontendPort = parseInt(env.BEEBOARD_FRONTEND_PORT || '3200', 10)
  const backendPort = parseInt(env.BEEBOARD_BACKEND_PORT || '8000', 10)

  return {
    define: {
      'import.meta.env.VITE_APP_VERSION': JSON.stringify(appVersion)
    },
    plugins: [
      vue(),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: frontendPort,
      strictPort: false,
      proxy: {
        '/api': {
          target: `http://127.0.0.1:${backendPort}`,
          changeOrigin: true,
        },
        '/uploads': {
          target: `http://127.0.0.1:${backendPort}`,
          changeOrigin: true,
        }
      }
    }
  }
})
