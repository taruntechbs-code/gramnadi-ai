import { useQuery } from '@tanstack/react-query'

import { getPlatformHealth } from '../services/platform'

export const usePlatformHealth = () =>
  useQuery({
    queryKey: ['platform', 'health'],
    queryFn: getPlatformHealth,
    staleTime: 30_000,
    retry: 1,
  })
