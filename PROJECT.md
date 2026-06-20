# Corvette Website — Project Brief

> **For Claude in VS Code:** This is the source of truth for the project. Build in order — structure first, then features, then styling. Section 4 defines the build phases; do not jump ahead to later phases until earlier ones are confirmed working.

---

## 0. One-line purpose

A personal one-stop hub for everything related to my **red 1984 Chevrolet C4 Corvette** — repairs (planned, in progress, done), a wish list of parts to buy, specs, a maintenance schedule, expense analytics, notes, and important links/forums.

**This site is:** a private build-log and reference tool for my car that I can optionally share (read-only) with friends and family.

---

## 1. Structure

### Site type
A personal tool to input, track, and reference everything about a car I love to work on and drive. Single owner/admin, with a read-only mode for guests.

### Pages (in sidebar order)
1. **Dashboard** — at-a-glance overview (active repairs, next maintenance due, total spent, wish list count)
2. **Repairs & Upgrades** — track planned/in-progress/done items with full detail
3. **Maintenance** — recurring and one-time maintenance log with scheduling
4. **Wish List** — queue of future repairs/maintenance items, promotable to those pages
5. **Expenses** — analytics dashboard showing spend pulled from Repairs & Upgrades
6. **Specs** — static read-only page with car specs and history
7. **Resources** — important links and forums
8. **Notes** — free-form notes in a folder structure

### Navigation model
Multi-page site with a persistent sidebar navigation.

### Technical shape
Python + Flask backend, SQLite database, plain HTML/CSS/JS frontend. Hosted on **Render**.

### UI pattern (established)
All add/edit interactions use a **slide-in drawer from the right** — not a separate page or inline form. A dark overlay covers the rest of the page. The same drawer is reused for both add and edit, with the form action and button text swapped via JavaScript.

---

## 2. Page-by-page design requirements

### Repairs & Upgrades ✓ Built
**Fields per entry:**
- Title
- Status (Not Started / In Progress / Done)
- Category (Engine / Transmission / Suspension / Steering / Exterior/Cosmetic / Interior / Lights/Lamps / Other)
- Cost ($)
- Start Date + toggle for "unknown start date"
- Finish Date + toggle for "unknown finish date"
- Total Time Taken
- Paid for service (labor) — yes/no toggle
- Mechanic / Shop Name
- Parts/Materials Vendor
- Purchase Link (URL) — displays as ↗ icon inline with title
- Notes

**Behavior:**
- Table of all entries shown at top of page
- Filter by status; sort by date added, cost, start date, finish date, or title
- "Add Repair / Upgrade" button opens slide-in drawer from right
- Edit button on each row opens same drawer pre-filled with that entry's data
- Delete with confirmation prompt
- Mechanic column in table shows name + "(paid)" in red if service was paid

---

### Specs ✓ Built
**Read-only page — no user input.**

Two-column layout matching Car and Driver's format, with a short history blurb at the top (red left-border card).

**Blurb (top of page):**
Unveiled in March 1983, the 1984 Corvette marked the debut of the C4 generation — a ground-up redesign of America's sports car after twelve years of the C3. The new body was lower, sleeker, and more aerodynamic, with a clamshell hood and the first digital instrument cluster ever offered in a Corvette. Rather than chasing horsepower, GM prioritized handling for the C4's debut year — the result could pull 0.90 g on the skidpad, outgripping nearly everything on the road at the time. The optional Doug Nash 4+3 overdrive gave drivers the feel of a 4-speed manual with the fuel economy of an automatic — a distinctly 1980s solution, technically ambitious and unapologetically American.

**Specs to display (two-column layout):**

Column 1:
- Vehicle Type: Front-engine, rear-wheel-drive, 2-passenger, 2-door targa
- Price as Tested (C/D Est.): $28,000
- Engine Type: Pushrod 16-valve V-8, iron block and heads, 2x1-bbl Rochester throttle-body fuel injection
- Displacement: 350 in³, 5733 cm³
- Power: 205 hp @ 4300 rpm
- Torque: 290 lb-ft @ 2800 rpm
- Transmission: 4-speed manual with Doug Nash 4+3 electronic overdrive
- Suspension (F/R): struts/multilink
- Brakes (F/R): 11.5-in vented disc / 11.5-in vented disc
- Tires: Goodyear Eagle VR50, P255/50VR-16

Column 2 — Dimensions:
- Wheelbase: 96.0 in
- Length: 176.5 in
- Width: 71.0 in
- Height: 46.9 in
- Passenger Volume: 49 ft³
- Cargo Volume: 18 ft³
- Curb Weight: 3300 lb

Column 2 — C/D Test Results:
- 0–60 mph: 6.7 sec
- 0–100 mph: 20.0 sec
- 0–110 mph: 27.2 sec
- Top gear, 30–50 mph: 3.5 sec
- Top gear, 50–70 mph: 5.2 sec
- 1/4 mile: 15.2 sec @ 90 mph
- Top speed: 138 mph
- Braking, 70–0 mph: 173 ft
- Roadholding, 200-ft-dia skidpad: 0.90 g

Column 2 — EPA Fuel Economy:
- Combined/City/Highway: 20/16/28 mpg

**Link at bottom:** [Car and Driver Road Test](https://www.caranddriver.com/reviews/a15141822/1984-chevrolet-corvette-c4-archived-road-test/)

---

### Maintenance ✓ Built
**Fields per entry:**
- Task name
- Status (Pending / Done)
- Start Date + toggle for "unknown start date"
- Finish Date + toggle for "unknown finish date"
- Total Time Taken
- Paid for service (labor) — yes/no toggle
- Mechanic / Shop Name
- Parts/Materials Vendor
- Purchase Link (URL)
- Recurring toggle (on/off)
  - If recurring: frequency in miles (optional) + frequency in months min + months max (optional)
  - When marked Done with recurring + finish date + frequency set, auto-calculates next due date
- Notes

**Behavior:**
- Slide-in drawer for add/edit (same pattern as Repairs)
- Table shows: task, status badge, recurring info + frequency, next due date, last done date, time taken, parts vendor, mechanic
- Filter by status and recurring; sort by next due date, last done, task name, or date added
- Delete with confirmation prompt

---

### Expenses — Partial (analytics only)
**No data entry on this page.** Costs are pulled automatically from Repairs & Upgrades entries.

**Currently shows:**
- Total spend (all time, from repairs)
- Line-item list of repair costs with completion date

**Planned analytics (Phase 1 remaining):**
- Spend by month (bar or line chart)
- Trending spend (going up or down?)
- Spend by category

> Note: There is no separate `expenses` table in the database. All cost data lives on the `repairs` table (`cost` field).

---

### Wish List ✓ Built
A queue of future actions — items that will eventually be moved into Repairs & Upgrades or Maintenance.

**Fields per entry:**
- Name
- Type (Repair/Upgrade or Maintenance)
- Category (Engine / Transmission / Suspension / Steering / Exterior/Cosmetic / Interior / Lights/Lamps / Other)
- Estimated Price ($)
- Link (URL) — displays as ↗ icon
- Notes

**Behavior:**
- Slide-in drawer for add/edit
- Filter by type and category
- **→ Repairs button** on each row: moves item to Repairs & Upgrades with "Not Started" status, pre-fills title/category/cost/link/notes, and removes it from the wish list
- Edit and delete with confirmation

---

### Resources
- User can add, edit, and delete links
- Fields: Title, URL, Description
- Edit/delete not yet implemented

---

### Notes
- User can add, edit, and delete notes
- Notes are organized in folders
- Fields: Title, Folder, Content
- Edit/delete not yet implemented

---

## 3. Database schema

```
repairs:     id, title, status, category, cost, start_date, start_date_unknown,
             finish_date, finish_date_unknown, time_taken, paid_for_service,
             mechanic, vendor, purchase_link, notes

maintenance: id, task, status, start_date, start_date_unknown, finish_date,
             finish_date_unknown, time_taken, paid_for_service, mechanic,
             vendor, purchase_link, recurring, frequency_miles,
             frequency_months_min, frequency_months_max, next_due_date, notes

wishlist:    id, name, type, category, estimated_price, link, notes

resources:   id, title, url, description

notes:       id, title, folder, content, created_at
```

> No `expenses` table. Cost data lives in `repairs.cost`.
> No `python-dateutil` dependency — next due date uses Python stdlib (calendar module).

---

## 4. Styling

> Apply in **Phase 3** only — after all features are confirmed working.

### Overall feel
A website styled to look like the graphical interface of a mid-to-late-80s personal computer — the era of the first Mac and early Windows. Boxy, monochrome-leaning, and utilitarian, but rendered crisply and deliberately rather than looking genuinely old or broken.

### Color palette
Built almost entirely on **platinum and silver greys** — a light grey base (around `#C0C0C0` to `#DFDFDF`), with mid and dark greys for depth. **Near-black text** throughout for high contrast. Color is used sparingly: a single bold accent — **Corvette red** — appears only on key elements like active states, highlights, or the logo.

### Beveled 3D edges (the signature detail)
Elements have a "chiseled" pseudo-3D look created with hard light-and-dark borders rather than soft shadows. Raised elements (buttons, panels) catch light on the top-left and shadow on the bottom-right; recessed elements (text fields, content wells) invert that. No gradients, no blur — just sharp 1–2px highlight/shadow lines.

### Typography
**Pixel/bitmap fonts** for headers and system-style labels. Body text stays in a clean, legible companion face.

### Small period details
Chunky scrollbars with bevels, dotted focus outlines, square (not rounded) corners everywhere, tight checkbox/radio controls, and an optional dark "boot" or "login" screen as an entry point.

### The crucial modifier
All of the above is executed with **modern polish** — a real layout grid, generous and consistent spacing, clean alignment, and accessible contrast. The *look* is 1985; the *craft* is current.

### Helpful starting point
CSS libraries like **98.css**, **7.css**, or **XP.css** provide authentic beveled-grey widget styling to borrow from.

---

## 5. Build order & guardrails

### Phase 1 — Core structure + data (MVP)
1. ✓ Scaffold pages, navigation, and database schema
2. ✓ Basic CRUD on all pages
3. ✓ Repairs & Upgrades — full rebuild with drawer
4. ✓ Specs — static page
5. ✓ Maintenance — full rebuild with drawer
6. ✓ Wish List — full rebuild with drawer + promote button
7. Expenses — add charts and category breakdown
8. Resources — add edit/delete
9. Notes — add edit/delete
10. Dashboard — wire up live data from all sections

### Phase 2 — Accounts & sharing
11. Admin login + viewer (read-only) role
12. Lock financial info behind unlock for viewers

### Phase 3 — Styling
13. Apply the visual design from Section 4

### Phase 4 — Advanced / nice-to-have
14. Forum/resource querying
15. Viewer activity tracking/analytics

### Constraints
- Keep components small and reusable
- Build with seed data so every page is testable before real content exists
- Don't implement styling before Phase 3
- Flag any feature that adds significant complexity before building it
- Always use `[dict(r) for r in rows]` when passing SQLite results to Jinja `tojson`
- Always use `data-item='{{ item | tojson }}'` (single quotes) to pass JSON to JS, read with `JSON.parse(el.dataset.item)`

---

## 6. Open questions / parking lot

- How important is mobile vs. desktop for day-to-day use in the garage?
- Which other cars do I most want to compare specs against?
- Should the Wish List "→ Repairs" button also support promoting to Maintenance?
