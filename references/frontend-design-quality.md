# Frontend design quality: avoid generic output, design for people

Use this when building or reshaping UI: new screens, components, states, forms, copy, or styling. The goal is an interface that fits its subject and its users, not one that looks like every other generated page.

## 0. When this applies (and when it does not)
1. **The existing design system wins.** If the repository already has tokens, components, a style guide, or established screens, reuse them and match them. Do not restyle unrelated screens, swap fonts, or add a UI library to change the look.
2. **An explicit brief wins.** If the user or product specifies a direction (even one listed below as a common default), follow it.
3. Apply the rest of this file to new surfaces without an established design, to design requests, and to the parts of an existing screen you are building (states, copy, accessibility) where the system gives no answer.
4. Component-library defaults are a starting point. Customize tokens (color roles, radius, type, spacing) so the product does not look like the library's demo.

## 1. Start from intent, not from a template
Before writing UI, write three lines (in the reply or the notes you keep): who uses this, the one primary task, and the context (device, frequency, data density, tone). If the request does not say, state your assumption. A back-office table, a checkout, and a public landing page need different density, tone, and emphasis.

## 2. Common tells of generated UI (defaults, not choices)
Avoid these unless the brief or the content justifies them. Each is acceptable when chosen on purpose for this subject; the problem is using them because they are the default.
- **Template page shape:** a centered headline with a gradient word, two buttons, then three identical icon cards; a "trusted by" row of fake logos; a closing call-to-action band.
- **Visual defaults:** purple-to-blue gradients, frosted-glass panels, glowing shadows, decorative blobs, one border radius and one soft shadow on everything, every section turned into a card.
- **Palette clichés:** warm cream background with a serif display face and a clay/terracotta accent; near-black with a single acid-green or vermilion accent; hairline-ruled "newspaper" columns with zero radius.
- **Template chrome:** an all-caps tracked-out label above every heading; numbered markers (01 / 02 / 03) on content that is not a sequence; meta strings joined with middle dots; "WORD: fragment" labels; an arrow appended to every link; one word of a headline in a different color or italic.
- **Placeholder content:** lorem ipsum, "John Doe", invented statistics ("10k+ users"), invented testimonials, stock faces, logos of companies that are not customers. Never fabricate proof, numbers, quotes, or customer names. Use clearly marked placeholders or ask for the real content.
- **Marketing filler:** "seamless", "unlock the power", "supercharge", "revolutionize", "cutting-edge". Say what the thing does, plainly.
- **Motion by default:** every section fading up on scroll, every card lifting on hover, bouncing or pulsing icons, `transition: all`.
- **Generic states:** "Something went wrong", "Submit", "Click here", an empty screen with no next step.

## 3. Make deliberate, specific choices
- **One design plan, kept small.** Name the color roles (background, surface, text, muted text, border, primary, danger, success) with real values; one or two type families and a scale of 4 to 6 sizes; a spacing scale (for example a 4 or 8 point base); radius and elevation rules; then reuse them as variables. Check each choice against "would I pick this for any similar page?" and change the ones that are only defaults.
- **Spend boldness in one place.** Let one element carry the personality and keep the rest disciplined. Remove decoration that does not serve the task.
- **Structure carries meaning.** Borders, dividers, numbering, and labels should encode information (grouping, sequence, status), not decorate.
- **Typography:** a clear hierarchy with few sizes and weights, line length under about 80 characters, adequate line height (a little more for serif body text). Pick faces deliberately; do not add font dependencies or external font URLs without approval and a fallback stack.
- **Color:** limited palette, meaning not carried by color alone, text contrast of at least 4.5:1 (3:1 for large text and UI boundaries). Check contrast with a tool or compute it; if you cannot, choose from known-safe pairs and say it is unchecked.
- **Density matches the product:** data tools favor scannability and compact rows; marketing favors emphasis and space. Consistency beats novelty inside an application; distinctiveness belongs to brand and marketing surfaces.

## 4. Design for the person using it
- **Hierarchy:** one primary action per view; group related things with proximity and spacing rather than boxes around everything.
- **Words are interface.** Write from the user's point of view, in their language and the product's voice. Buttons say what will happen ("Save changes", "Delete 3 files"), and the same action keeps the same name across the flow (the "Publish" button produces "Published"). Errors say what happened and how to fix it, without blaming the user or apologizing vaguely. Empty states say what the area is for and offer the next step. Sentence case, plain verbs, no filler.
- **Every state exists:** loading (skeleton or spinner to suit the wait), empty, partial, error with a recovery action, success, disabled (with the reason visible), and permission denied. Confirm destructive actions with specifics and offer undo where possible.
- **Forms:** visible labels (a placeholder is not a label), appropriate input types and autocomplete hints, validation timing that does not scold while typing, errors next to the field and summarized for screen readers, input preserved on failure, sensible defaults, required vs optional stated, no double submit.
- **Real content in the design:** test with long names, missing values, many rows, zero rows, very long words, and the languages and number/date formats the product serves. Text in other languages is often longer.
- **Responsive by default:** works at phone width without horizontal scrolling; tables become priority columns, stacked rows, or a scroll container; touch targets comfortably tappable.
- **Accessibility floor (not an extra):** semantic elements first (button, a, label, headings in order, landmarks); everything operable by keyboard with a visible focus indicator; meaningful alt text (empty alt for decoration); do not remove outlines without replacing them; respect reduced-motion and zoom/text-size settings; announce dynamic changes politely.
- **Motion with purpose:** use it to show what changed (open, expand, confirm), keep it short (roughly 150 to 250 ms), and turn it off or reduce it for people who ask. One orchestrated moment beats scattered effects.
- **Performance is part of the design:** size images, avoid layout shift, and keep above-the-fold work light.

## 5. Process
1. Inspect what exists (components, tokens, screenshots, copy tone). Reuse before creating.
2. Write the three-line intent and, for new surfaces, the small design plan from section 3.
3. Build the smallest set of components; keep CSS specificity simple so rules do not cancel each other.
4. Exercise states with realistic and extreme data.
5. Review against the checklist below. If your environment can render the UI, look at it at phone and desktop widths and fix what you see; if not, mark visual review `NOT RUN` and say so.
6. Optional mechanical pass (advisory, heuristic): `python scripts/ui_slop_scan.py <paths>` flags placeholder text, buzzwords, default gradients, motion defaults, and common accessibility slips. It cannot judge taste; a clean scan does not mean the design is good.

## 6. Self-review checklist
- [ ] Matches the existing design system, or has an explicit plan where none exists.
- [ ] I can state the audience, the primary task, and what makes this design specific to the subject.
- [ ] No template page shape, default gradient, or all-cards layout used out of habit.
- [ ] No fabricated numbers, quotes, logos, or customers; no lorem ipsum.
- [ ] Copy is specific, in the user's language and voice; buttons and errors say what happens.
- [ ] Loading, empty, error, success, disabled, and denied states handled.
- [ ] Forms have visible labels, helpful errors, preserved input.
- [ ] Keyboard, focus, contrast, alt text, reduced motion, and reflow at narrow width checked or marked `NOT RUN`.
- [ ] Motion is purposeful and limited.
- [ ] No new dependency, font, or external asset added just for styling.
- [ ] Anything I could not look at or measure is reported as `NOT RUN` or `UNVERIFIED`.
