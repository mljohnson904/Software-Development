# usage-monitor

A Claude Code mod that keeps your usage on screen: a context-window bar, the 5-hour and 7-day rate-limit bars, session cost, and a row of 🦀 for subagents (a sleeping 🦀💤 once one finishes). It draws as a pane and as a band above the prompt, and puts a short summary in the status line. Bars are green, yellow from 70% and red from 90%.

## Use it on your own computer

1. Copy this `usage-monitor` folder into `C:\Users\michael.johnson5\Desktop\Claude Mods\`.
2. Start Claude Code from a terminal with the mod loaded:

   claude --plugin-dir "C:\Users\michael.johnson5\Desktop\Claude Mods\usage-monitor"

3. Run `/usage-pane` to reopen the pane if you close it.

The mod reads `$.session.usage()` and `$.agent.list()`, and stores nothing outside the session.
