# Corvette Website — Project Brief

> **For Claude in VS Code:** This is the source of truth for the project. Build in order — structure first, then features, then styling. Section 4 defines the build phases; do not jump ahead to later phases until earlier ones are confirmed working.

---

## 0. One-line purpose

A personal one-stop hub for everything related to my **red 1984 Chevrolet C4 Corvette** — repairs (planned, in progress, done), a wish list of parts to buy, specs, a maintenance schedule, expense tracking, notes, and important links/forums.

**This site is:** a private build-log and reference tool for my car that I can optionally share (read-only) with friends and family.

---

## 1. Structure

### Site type
A personal tool to input, track, and reference everything about a car I love to work on and drive. Single owner/admin, with a read-only mode for guests.

### Pages
- **Landing / Dashboard** — at-a-glance overview (active repairs, next maintenance due, recent activity)
- **Specs** — view/edit my car's specs; compare against other cars
- **Maintenance Schedule** — upcoming + completed maintenance log
- **Repairs & Upgrades** — track planned/in-progress/done items with cost and time
- **Expenses** — manual cost entries to track spending
- **Wish List** — categorized parts to buy, with links and prices
- **Resources** — important links and forums
- **Notes** — free-form notes in a folder structure

### Navigation model
Multi-page site with a persistent navigation pane (sidebar or top nav).

### Interactive features
- Repair/upgrade tracker with status (Not Started / In Progress / Done) and dollar amounts
- Spec comparison tool (my car vs. any other car)
- Expense logging via manual entry
- Categorized wish list with external links and prices
- Notes with folder structure
- Admin login (edit access) vs. viewer mode (read-only)
- Financial info locked behind access unless unlocked
- Basic tracking of what viewers looked at — **later phase**

### Technical shape
Firebase (Firestore for database, Firebase Auth for login) + plain HTML/CSS/JS frontend. Hosted on GitHub Pages. No file uploads needed.

### Content readiness
Most content isn't ready yet, but I can supply it on the fly. Build with placeholder/seed data so every page is testable before real content goes in.

---

## 2. User stories

> Single primary user (me = **admin**), plus a read-only **viewer** role for guests. Stories are grouped by feature.

### Repairs & upgrades
- As an admin, I want to add repairs/upgrades I plan to make, **track their status** (Not Started / In Progress / Done), and **assign a dollar amount** to each.
- As an admin, I want to **timestamp** when I did a repair or maintenance task, and record **how long it took**.
- As an admin, I want to **retroactively log past repairs**, and if I don't know the exact month/day, I can enter just the year.

### Specs
- As an admin or viewer, I want to **view my car's specs** and **compare them to another car** — horsepower, torque, 0–60 time, dimensions, sticker price, color, etc.
- As an admin, I want to **update my car's specs** as things change.

### Maintenance
- As an admin, I want to see a **maintenance schedule** (what's due) and a **log of completed maintenance** with timestamps and time taken.
- As a viewer, I want to **see the maintenance schedule** and the repair list (including Not Started / In Progress status).

### Expenses
- As an admin, I want to **enter custom amounts** to track expenses.

### Wish list
- As an admin, I want to keep a **wish list** of parts to buy, each with a **link and price**, **categorized** by type: Exterior/Cosmetic, Interior, Lights/Lamps, Engine, Transmission, Suspension, Steering, etc.

### Resources
- As an admin, I want to keep a list of **important links and forums** related to my car.

### Notes
- As an admin, I want to **write notes organized in a folder structure**.

### Access & roles
- As an admin, I want to **log in** so viewers can't make changes.
- As a viewer, I want **financial info hidden** unless access is unlocked.
- As an admin (later phase), I want to **see what viewers looked at** on the site.

---

## 3. Styling

> **Aesthetic only — standard website functionality.** This is a visual skin, not an interface model. The site functions as a normal scrolling, multi-page website. Apply this look in **Phase 3**, layered over the plain pages built earlier. Build earlier phases with a neutral, unstyled layout.

### Overall feel
A website styled to look like the graphical interface of a mid-to-late-80s personal computer — the era of the first Mac and early Windows. Boxy, monochrome-leaning, and utilitarian, but rendered crisply and deliberately rather than looking genuinely old or broken.

### Color palette
Built almost entirely on **platinum and silver greys** — a light grey base (around `#C0C0C0` to `#DFDFDF`), with mid and dark greys for depth. **Near-black text** throughout for high contrast. Color is used sparingly: a single bold accent — **Corvette red** — appears only on key elements like active states, highlights, or the logo.

### Beveled 3D edges (the signature detail)
Elements have a "chiseled" pseudo-3D look created with hard light-and-dark borders rather than soft shadows. Raised elements (buttons, panels) catch light on the top-left and shadow on the bottom-right; recessed elements (text fields, content wells) invert that. No gradients, no blur — just sharp 1–2px highlight/shadow lines.

### Typography
**Pixel/bitmap fonts** for headers and system-style labels (blocky, low-resolution letterforms with visible square pixels). Body text stays in a clean, legible companion face so longer content remains readable.

### Small period details
Chunky scrollbars with bevels, dotted focus outlines, square (not rounded) corners everywhere, tight checkbox/radio controls, and an optional dark "boot" or "login" screen as an entry point.

### The crucial modifier
All of the above is executed with **modern polish** — a real layout grid, generous and consistent spacing, clean alignment, and accessible contrast. The *look* is 1985; the *craft* is current. It should read as a deliberate, refined homage, not a literal old web page.

### Helpful starting point
CSS libraries like **98.css**, **7.css**, or **XP.css** provide authentic beveled-grey widget styling to borrow from (use the visual styling, ignore any interactive/windowing behavior).

### References
_Add 1–3 URLs of sites whose look you like:_
-

---

## 4. Build order & guardrails

Build in phases. **Get Phase 1 working and confirmed before starting Phase 2.** Styling comes last.

### Phase 1 — Core structure + data (MVP)
1. Scaffold pages, navigation, and the Firestore data schema.
2. Build the core CRUD features with seed/placeholder data:
   - Repairs & upgrades (status, cost, timestamp, time taken, retroactive/year-only dates)
   - Specs (view/edit + compare)
   - Maintenance schedule + completed log
   - Wish list (categorized, link + price)
   - Expenses (manual amounts)
   - Notes (folder structure)
   - Resources (links)
3. Landing/Dashboard pulling from the above.

### Phase 2 — Accounts & sharing
4. Admin login + viewer (read-only) role using Firebase Auth.
5. Lock financial info (costs, expenses, prices) behind unlock for viewers.

### Phase 3 — Styling
6. Apply the visual design from Section 3, once structure and features are confirmed.

### Phase 4 — Advanced / nice-to-have
7. Forum/resource querying.
8. Viewer activity tracking/analytics.

### Constraints
- Keep components small and reusable (e.g. one card component reused for repairs and wish-list items).
- Keep the stack simple and easy to run locally / host cheaply.
- Build with seed data so every page is testable before real content exists.
- Don't implement styling before Phase 3.
- Flag any feature that adds significant complexity before building it, so I can decide whether it's worth it now.

---

## 5. Open questions / parking lot

- Confirm styling direction (80s retro-digital vs. modern dark) and add reference URLs.
- How important is mobile vs. desktop for day-to-day use in the garage?
- Which other cars do I most want to compare specs against? (helps seed the compare feature)
