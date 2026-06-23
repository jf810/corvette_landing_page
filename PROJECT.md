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

### Specs & Details ✓ Built
**Read-only page — no user input.**

**Source of truth:** `corvette_specs_and_details.md` — decoded SPID label, VIN breakdown, RPO codes, and GM fluid chart. All data hard-coded into the HTML template from that document.

**Layout:** Window-sticker style — dark section headers, grouped label/value rows with horizontal dividers. Same CSS pattern (`sd-*` classes) used for all sections.

**Page sections:**

**1 — Performance Specs** (from C&D road test)
- Vehicle (type, body style, price as tested)
- Engine (L83 5.7L Cross-Fire Injection V8, displacement, power, torque)
- Drivetrain (Doug Nash 4+3, rear axle ratio, suspension, brakes, tires)
- Dimensions — two-column pairs (wheelbase/length, width/height, volumes, weight/fuel tank)
- C/D Test Results — two-column pairs (0–60, 0–100, ¼ mile, top speed, braking, skidpad)
- EPA Fuel Economy (city/highway, combined)
- Source link to Car and Driver road test

**2 — My Car — Trim & Color Codes** (from SPID label)
- Exterior: color (Bright Red), paint code (WA8551), paint system, color codes (33U/33L), body style callout (targa/hatchback)
- Interior: color (Carmine Red leather), code (742), trim code (74I), seat detail (perforated leather, sport seats AG9/A51)
- RPO codes grouped by category: Engine & Drivetrain (L83, MM4, MK2, HE3), Comfort (AG9, A42, A51, AU3, K34), Audio (UQ4, UU8), Electrical/Cooling (K61, V01), Wheels (QZD), Emissions (NA5, NB1, V73)

**3 — Fluids & Capacities** (from GM owner's manual)
- Capacities table (two-column pairs): engine oil drain/filter, cooling, fuel, manual trans, OD unit, differential
- Recommended fluids table (3 columns: system | GM/factory spec | currently in use)

**4 — Vehicle Identification**
- Year / Make / Model, Assembly Plant (Bowling Green, KY), Production Sequence (#135,728)
- VIN — hidden by default, click-to-reveal button
- License plate — hidden by default, click-to-reveal button
- Mileage as of date (hard-coded, update manually in HTML)

**5 — Notes & Quirks**
- Shifter knob threading: 9/16-18
- L83 flat-tappet cam ZDDP note
- Doug Nash 4+3 split fluid note (different fluids for box vs. OD unit)
- Limited-slip rear axle friction modifier note

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

### Expenses ✓ Built
A standalone expense tracker with analytics. Data is entered directly — not pulled from Repairs & Upgrades automatically (though the Wish List promote flow creates an expense entry automatically, see below).

**Fields per expense entry:**
- Title
- Category (expanded set — see categories below)
- Cost ($)
- Purchase Month (YYYY-MM, stored as text; uses `<input type="month">`)
- Parts Vendor
- Mechanic / Shop
- Group (optional — links to a Group record; see Group System below)
- Link to Repair (optional FK to `repairs.id`)
- Link to Maintenance Task (optional FK to `maintenance.id`)
- Notes

**Analytics shown above the table:**
- **Key metrics row** — Total Spent / Avg Per Month / Avg Per Year
  - Avg per month = total ÷ number of months from first expense to today
  - Avg per year = avg per month × 12
- **Bar chart** — Monthly spend for last 12 months, full width, Y axis auto-scales to data. Rendered with Chart.js (CDN, no install).
- **Donut chart** — Spend by category, shown to the right of bar chart on desktop, stacked below on mobile.
- Charts update automatically whenever a new expense is saved.

**Category list (expense-specific, broader than Repairs):**
- Mechanical: Engine, Transmission, Drivetrain, Brakes, Suspension, Steering, Exhaust, Fuel System, Cooling System, Electrical
- Body & Interior: Interior, Exterior / Body, Glass & Trim, Lighting
- Maintenance Supplies: Fluids & Chemicals, Tires & Wheels, Filters, Belts & Hoses
- Ownership & Tools: Registration & Fees, Insurance, Storage, Tools & Equipment, Other

**Group System:**
Groups allow multiple expenses (and their linked repairs/maintenance tasks) to be organized under one project.
- Groups have a **type**: `R` (Repair/Upgrade) or `M` (Maintenance)
- Codes are auto-generated sequentially per type: first repair group = `R1`, second = `R2`; first maintenance group = `M1`, etc.
- Each expense within a group gets a stable **sub-number** assigned at creation time: `R1-1`, `R1-2`, `M2-3`, etc. The number never changes even if earlier entries are deleted, preserving a clean audit trail.
- Groups are displayed with a reference panel at the bottom of the Expenses page; individual groups can be deleted (expenses are unlinked but not deleted).

**Bidirectional group cascade:**
When you change the group on any linked record, it propagates to all connected records:
- Change group on an **expense** → linked repair and/or maintenance task automatically update to the same group.
- Change group on a **repair** → all expenses with `repair_id` pointing to that repair update to the new group and get new sequential sub-numbers within the target group.
- Change group on a **maintenance task** → same cascade for expenses with `maintenance_id` pointing to that task.

**"+ Create New Group" inline:**
The Group dropdown in the Add/Edit drawer on Expenses, Repairs & Upgrades, and Maintenance all include a `+ Create New Group` option. Selecting it reveals a name field (and a type selector on the Expenses drawer). The group is created automatically when the form is saved — no need to visit a separate page.

**Behavior:**
- Slide-in drawer for add/edit (same pattern as Repairs and Maintenance)
- Expense table shown below charts with columns: Code, Title, Category, Cost, Month, Vendor, Group, Actions
- Delete with confirmation prompt

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
- **→ Promote button** on each row: opens a slide-in drawer with three options:
  1. **Move to** — Repair/Upgrade or Maintenance (defaults to match the item's type)
  2. **Group** — choose an existing group, `+ Create New Group` (reveals a name field), or no group
  3. Hitting **Promote →** does all of the following atomically:
     - Creates a new group (if requested) with the correct type code (R or M)
     - Creates a Repair or Maintenance entry pre-filled with the wishlist item's name, category, cost, link, and notes
     - If the wishlist item had an estimated price: also creates an Expense entry with `repair_id` or `maintenance_id` set, linked to the same group, and assigned the next sub-number within that group
     - Removes the item from the wish list
     - Redirects to the Repairs or Maintenance page
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
             mechanic, vendor, purchase_link, notes, group_id → groups.id

maintenance: id, task, status, start_date, start_date_unknown, finish_date,
             finish_date_unknown, time_taken, paid_for_service, mechanic,
             vendor, purchase_link, recurring, frequency_miles,
             frequency_months_min, frequency_months_max, next_due_date, notes,
             group_id → groups.id

expenses:    id, title, category, cost, purchase_month (YYYY-MM text),
             vendor, mechanic, notes,
             group_id → groups.id,
             group_expense_num (stable sub-number within group, e.g. 1, 2, 3),
             repair_id → repairs.id (optional direct link),
             maintenance_id → maintenance.id (optional direct link)

groups:      id, name, type ('R' or 'M'), code (auto: R1/R2… or M1/M2…), notes

wishlist:    id, name, type, category, estimated_price, link, notes

resources:   id, title, url, description

notes:       id, title, folder, content, created_at
```

**Schema migration approach:** New columns are added to existing tables via `ALTER TABLE … ADD COLUMN` inside `init_db()`, wrapped in try/except to be safe on re-runs. The `groups` and `expenses` tables use `CREATE TABLE IF NOT EXISTS`. `init_db()` is called at module load time so migrations run automatically on every server start.

> No `python-dateutil` dependency — next due date uses Python stdlib (calendar module).
> Chart.js loaded via CDN (jsdelivr) on the Expenses page only — no npm or build step needed.

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
3. ✓ Repairs & Upgrades — full rebuild with drawer; group linkage + cascade
4. ✓ Specs & Details — window-sticker layout with performance specs, trim/color codes, fluids, vehicle ID (hidden VIN/plate), and notes
5. ✓ Maintenance — full rebuild with drawer; group linkage + cascade
6. ✓ Wish List — full rebuild with drawer + promote flow (repair or maintenance, group, auto-expense)
7. ✓ Expenses — standalone expense tracker with bar chart, donut chart, key metrics, group system, and bidirectional cascade
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
- ~~Should the Wish List "→ Repairs" button also support promoting to Maintenance?~~ **Done** — promote flow now supports both Repair and Maintenance, with group selection and auto-expense creation.
- Phase 2 (Repairs & Maintenance group linkage on those pages) is fully complete — groups appear as a column in both tables and are selectable in the add/edit drawers.
