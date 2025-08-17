import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://bpomacnqaqzgeuahhlka.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwb21hY25xYXF6Z2V1YWhobGthIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0NTcyMjUsImV4cCI6MjA3MTAzMzIyNX0.wiDqoFa0KjqE_pRnZIGILmpVJ_3-xZb4dSURCyzDNTs'

// Create a single Supabase client instance to avoid multiple GoTrueClient instances
export const supabase = createClient(supabaseUrl, supabaseAnonKey)