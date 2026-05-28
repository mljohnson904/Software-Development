# Paper Trading Coach (MVP)

This is paper trading practice only and not financial advice.

## Run locally
```bash
npm install
npm run dev
```

## Build
```bash
npm run build
npm run preview
```

## Deploy
- **Vercel:** import repo and set root to `paper-trading-coach`.
- **GitHub Pages:** build and publish `dist/`.

## Features
- Mobile-first dark dashboard + bottom nav.
- Daily Command Center checklists.
- TradingView embeds (5M + 1M) with checklist.
- Trade journal with risk/R calculations and warnings.
- Stats summary, rules, roadmap, weekly review.
- Reminders + browser notification permission + ICS downloads.
- Settings backup/restore JSON and reset.

## TradingView note
Set Heikin Ashi, 100 EMA, and volume manually in the TradingView widget if not auto-applied.

## Calendar reminder import
Use buttons on Reminders page to download `.ics` and import into Google/Apple/Outlook calendar.
