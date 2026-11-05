import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Crab, Snap } from '../types'

const snap = atom<'usage-monitor', 'snap'>({ plugin: 'usage-monitor', key: 'snap' } as const, null)

const crabs = atom<'usage-monitor', 'crabs'>({ plugin: 'usage-monitor', key: 'crabs' } as const, [])

const isHidden = atom<'usage-monitor', 'isHidden'>({ plugin: 'usage-monitor', key: 'isHidden' } as const, false)

const PANE = 'usage-monitor'

const EIGHTHS = ['', '▏', '▎', '▍', '▌', '▋', '▊', '▉']

// Smooth bar: whole blocks plus one partial block, then a thin track.
const bar = (pct: number, width = 20) => {
  const eighths = Math.round((Math.max(0, Math.min(100, pct)) / 100) * width * 8)
  const full = Math.floor(eighths / 8)
  const part = EIGHTHS[eighths % 8] ?? ''
  const filled = '█'.repeat(full) + part
  return { filled, track: '─'.repeat(Math.max(0, width - filled.length)) }
}

const until = (iso: string | undefined, now: number) => {
  const ms = iso ? Date.parse(iso) - now : NaN
  if (!Number.isFinite(ms) || ms <= 0) return ''
  const m = Math.floor(ms / 60000)
  const d = Math.floor(m / 1440)
  const h = Math.floor((m % 1440) / 60)
  return d > 0 ? `resets ${d}d ${h}h` : h > 0 ? `resets ${h}h ${m % 60}m` : `resets ${m}m`
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
  const now = await $.clock.now()

  const rows: { key: string; name: string; pct: number; note: string }[] = []
  if (s.percent !== null) {
    rows.push({
      key: 'ctx',
      name: 'Context',
      pct: s.percent,
      note: s.tokens !== null ? `${Math.round(s.tokens / 1000)}k / ${Math.round(s.window / 1000)}k` : '',
    })
  }
  for (const l of s.limits) {
    rows.push({ key: l.kind, name: label(l.kind), pct: l.percentUsed, note: until(l.resetsAt, now) })
  }

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="cyan" paddingX={1}>
      <Box justifyContent="space-between">
        <Text bold color="cyan">◆ USAGE</Text>
        {s.usd !== null && <Text color="magenta">${s.usd.toFixed(2)}</Text>}
      </Box>
      {rows.map(row => {
        const b = bar(row.pct)
        return (
          <Box key={row.key}>
            <Text bold>{row.name.padEnd(8)}</Text>
            <Text color={tint(row.pct)}>{b.filled}</Text>
            <Text dimColor>{b.track}</Text>
            <Text color={tint(row.pct)} bold>{` ${String(Math.round(row.pct)).padStart(3)}%`}</Text>
            <Text dimColor>{row.note ? `  ${row.note}` : ''}</Text>
          </Box>
        )
      })}
      {rows.length === 0 && <Text dimColor>No usage data yet</Text>}
      <Box>
        <Text bold>{'Agents'.padEnd(8)}</Text>
        {running > 0 ? (
          <Text color="green">● {running} running</Text>
        ) : (
          <Text dimColor>○ idle</Text>
        )}
        {crabList.length > 0 && <Text> </Text>}
        {crabList.slice(-12).map(c => (
          <Text key={c.id} dimColor={c.isDone}>
            {c.isDone ? '🦀💤' : '🦀'}{' '}
          </Text>
        ))}
      </Box>
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
