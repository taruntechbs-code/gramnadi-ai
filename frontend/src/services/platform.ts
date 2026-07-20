import { apiClient } from '../api/client'

export interface PlatformHealth {
  status: string
}

export const getPlatformHealth = async (): Promise<PlatformHealth> => {
  const response = await apiClient.get<PlatformHealth>('/health')
  return response.data
}
