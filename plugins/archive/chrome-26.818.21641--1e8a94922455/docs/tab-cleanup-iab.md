# Tab Cleanup
- Agent-created tabs are temporary by default and close when the turn ends. Claimed user tabs are released back to the user by default.
- Call `tab.markDeliverable()` on a tab that should remain open as a user-facing output.
- Call `tab.markHandoff()` only when work should continue in a later turn.
- Marks are turn-scoped and the latest mark for a tab wins. Marked tabs survive the turn and are available in later turns. Mark tabs again in a later turn if it must survive that turn too.
- If the user asks to close all visible browser tabs in the in-app browser, do not rely on `browser.user.openTabs()` alone. Close current-session tabs from `browser.tabs.list()`, and claim and close released or user tabs from `browser.user.openTabs()`.
