/**
 * BeeBoard — Zentrale App-Konfiguration
 * Frontend bezieht APP_VERSION zentral aus der Root-Datei VERSION
 * (inject via Vite define: import.meta.env.VITE_APP_VERSION).
 * Wird in Sidebar, AuthView, AdminView, etc. verwendet.
 */

export const APP_NAME = 'BeeBoard'
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '2.1.0'
export const APP_DESCRIPTION = 'Reaktives Imkerei-Managementsystem'
