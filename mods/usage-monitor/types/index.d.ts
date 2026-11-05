export type Crab = { id: string; type: string; isDone: boolean }

export type Snap = {
  tokens: number | null
  window: number
  percent: number | null
  limits: { kind: string; percentUsed: number; resetsAt?: string }[]
  usd: number | null
}

declare module 'claude-code' {
  interface PluginState {
    'usage-monitor': { snap: Snap | null; crabs: Crab[]; isHidden: boolean }
  }
}
