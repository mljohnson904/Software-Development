import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Crab, Snap } from '../types'

const snap = atom<'usage-monitor', 'snap'>({ plugin: 'usage-monitor', key: 'snap' } as const, null)

const crabs = atom<'usage-monitor', 'crabs'>({ plugin: 'usage-monitor', key: 'crabs' } as const, [])

const isHidden = atom<'usage-monitor', 'isHidden'>({ plugin: 'usage-monitor', key: 'isHidden' } as const, false)

const PANE = 'usage-monitor'

const bar = (pct: number, width = 24) => {
  const n = Math.max(0, Math.min(width, Math.round((pct / 100) * width)))
  return '█'.repeat(n) + '░'.repeat(width - n)
}
const label = (k: string) =>
  k === 'five_hour' ? '5-hour' : k === 'seven_day' ? '7-day' : k
const tint = (p: number) => (p >= 90 ? 'red' : p >= 70 ? 'yellow' : 'green')

async function refresh($: any) {
  const u = await $.session.usage()
  const s: Snap = {
    tokens: u.context.tokens ?? null,
    window: u.context.window,
    percent: u.context.percent ?? null,
    limits: u.rateLimits.map((r: any) => ({
      kind: r.kind,
      percentUsed: r.percentUsed,
      resetsAt: r.resetsAt,
    })),
    usd: u.cost?.usd ?? null,
  }
  await update($, snap, () => s)
  const parts = [
    s.percent !== null ? `ctx ${Math.round(s.percent)}%` : null,
    ...s.limits.map(l => `${label(l.kind)} ${Math.round(l.percentUsed)}%`),
    s.usd !== null ? `$${s.usd.toFixed(2)}` : null,
  ].filter(Boolean)
  $.ui.status(parts.join(' · ') || undefined)
}

async function syncCrabs($: any) {
  const list = await $.agent.list()
  const ended = ['completed', 'failed', 'killed']
  const next: Crab[] = list.map((a: any) => ({
    id: a.id,
    type: a.type,
    isDone: ended.includes(a.status),
  }))
  await update($, crabs, old => {
    const seen = new Set(next.map(c => c.id))
    // keep crabs whose agent has dropped out of the list, marked done
    const gone = old.filter(c => !seen.has(c.id)).map(c => ({ ...c, isDone: true }))
    return [...gone, ...next].slice(-40)
  })
}

async function view($: any, e: any) {
  const { Box, Text } = $.ui.resolve(e)
  const s = await read($, snap)
  if (!s) return <Text dimColor>Waiting for usage data…</Text>
  const crabList = await read($, crabs)
  const running = crabList.filter(c => !c.isDone).length
  return (
    <Box flexDirection="column">
      {s.percent !== null && (
        <Text color={tint(s.percent)}>
          Context {bar(s.percent)} {Math.round(s.percent)}%
        </Text>
      )}
      {s.tokens !== null && (
        <Text dimColor>
          {s.tokens.toLocaleString()} / {s.window.toLocaleString()} tokens
        </Text>
      )}
      {s.limits.map(l => (
        <Text key={l.kind} color={tint(l.percentUsed)}>
          {label(l.kind)} {bar(l.percentUsed)} {Math.round(l.percentUsed)}%
        </Text>
      ))}
      {s.limits.length === 0 && <Text dimColor>No rate-limit data yet</Text>}
      {s.usd !== null && <Text>Session cost ${s.usd.toFixed(2)}</Text>}
      <Text bold>Subagents ({running} running)</Text>
      {crabList.length === 0 && <Text dimColor>none yet</Text>}
      {crabList.length > 0 && (
        <Box flexDirection="row" flexWrap="wrap">
          {crabList.map(c => (
            <Text key={c.id} dimColor={c.isDone}>
              {c.isDone ? '🦀💤' : '🦀'}{' '}
            </Text>
          ))}
        </Box>
      )}
    </Box>
  )

}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    $.ui.toast('Usage monitor loaded')
    void $.ui.open({ id: PANE, title: 'Usage' })
    await $.command.register({
      name: 'usage-pane',
      description: 'Show or hide the usage band above the prompt',
    })
    await refresh($)
    $.clock.every(2000, () => syncCrabs($))
    return next(e)
  })

  on('command.run', { command: 'usage-pane' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Usage' })
    await update($, isHidden, () => false)
    return { text: 'Usage pane opened.' }
  })

  on('session.measure', async ($, e, next) => {
    await refresh($)
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    await refresh($)
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) =>
    view($, e),
  )

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || (await read($, isHidden))) return next(e)
    return view($, e)
  })
}
