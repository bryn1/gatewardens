# DD2 Mechanics Decomposition — design input for the Gatewardens clone

Task: MC 11274.1.1 / card 11276 · Researcher profile · 2026-10-25
Clean-room study: only public wiki/community pages consulted; no original-game file touched.
Raw scrape evidence: `raw/scrape_*.json`, `raw/api_*.json` (same dir).

Method & source quality:
- Primary source: the community wiki `wiki.dungeondefenders2.com` (live-era DD2, pages fetched 2026-10-25), plus `dungeondefenders2.fandom.com`, `dungeondefenders.fandom.com` (DD1-series wiki, incl. the DD: Eternity F2P line), Steam discussions, and MediaWiki APIs where pages were Cloudflare-walled.
- Every VERIFIED row below carries the fetched URL and a verbatim quote from the fetched text (labels per citation-discipline: VERIFIED / OVERSTATED / INFERRED / UNVERIFIED / CONTRADICTED).
- EXCLUDED as citable evidence: `shapes.inc/fandom/dungeon-defenders-ii/gear-and-shards` — plausible content, but it is an AI-generated mirror with unverifiable provenance; used only as a lead, never quoted.
- The live wiki documents the FINAL (Chromatic-era) game state. 2015-era launch differs (smaller roster, pre-Chaos difficulty set); era-drift is called out per row.

Premise-check summary (the task's "confirm" items):
| Task premise | Verdict | Actual (fetched) |
|---|---|---|
| 4 attributes Strength/Dexterity/Intelligence/Endurance | CONTRADICTED | Neither DD2 nor the DD1-series wiki pages fetched show such attributes. DD2 hero stats = Hero Damage/Health, Ability Power/Resource, crit, speed (wiki Stats page + fandom hero data table). DD1 allocation stats = Hero Health/Hero Damage/Hero Speed/Hero Casting Rate + 4 Defense stats. |
| "Eternity Caches" loot boxes | CONTRADICTED (naming) | Fetched DD2 sources name Lockboxes (cosmetic, key-gated) and Victory Chests (free end-of-match loot). "Eternity" appears in the series only as DD: Eternity (F2P DD1), Eternia Crystal (mission objective), Eternity/Elemental lore names. |
| Tower XP during a mission + ability-tree picks at level thresholds | CONTRADICTED for DD2 | DD2 defenses are bought/upgraded with Green Mana (tiers, flat costs); the wiki's Defenses Interactions section documents only Build/Upgrade/Repair/Sell — no XP or level-threshold picks. |
| Difficulty tiers Normal/Nightmare/Hell | PARTLY | DD2 Campaign = "Normal or Hard"; live endgame = Chaos I–X Expeditions + Onslaught floors. Nightmare/Insane/Ruthless are DD1 tiers; no "Hell" tier found in either fetched list (grep of fetched difficulty/Expeditions pages). |
| Arrow/tesla/cannon/frost/lab tower families | PARTLY | DD2 organizes defenses by hero into 5 classes; named towers include Ballista/Skeletal Archer (arrow-likes), Tesla Coil/Rail Gun (tesla-likes), Cannonball/Flak Cannon (cannon-likes), Frostbite/Hailstorm (frost-likes). No "Lab" tower in the fetched lists. |
| Crafting workshops, legendary made at workshops | CONTRADICTED | DD2 has no player workshop-building; item improvement is NPC/inventory-based (Upgrading/Evolving/Advancing/Rerolling/Tinkering). Legendaries drop, they are not crafted. |
| Steam app 217030 | UNVERIFIED | Every fetched DD2 Steam URL is app 236110 (discussions, patchnotes on steamdb). 217030 did not resolve in any fetched source. |

## 1. Core loop

Mission → waves → victory chests → gear up → harder difficulty tier. VERIFIED:
- "The Campaign introduces the player to Dungeon Defenders 2. Campaign maps can be played in either Normal or Hard mode. After completing the Campaign, players should make their way over to Adventures, followed by Expeditions." — https://wiki.dungeondefenders2.com/wiki/Campaign
- "Victory Chests appears at the end of a match after all required waves has been completed. The chests provides bonus loot when opened." — https://wiki.dungeondefenders2.com/wiki/Victory_Chests
- "The War Table is the means by which players can start and join games in Dungeon Defenders 2. ... Interacting with the War Table brings up the World Map, which allows players to select maps based on which gamemode and difficulty they want." — https://wiki.dungeondefenders2.com/wiki/Tavern
- Endgame prestige loop: "Ascension is an account-wide system in which players continue to gain virtually limitless power past level 50." — https://wiki.dungeondefenders2.com/wiki/Ascension ; and an AP reset loop: https://wiki.dungeondefenders2.com/wiki/Ancient_Power (spend AP across heroes; multiplayer "Players with Spent AP will add their AP level for each skill together (max 10 pts per skill)" — Maps page).
- Clone implication: loop = select mission at hub War Table → defend cores vs fixed waves → chests/loot → rework gear → next Chaos tier / Onslaught floor.

## 2. Hero system

| Item | Value | Evidence |
|---|---|---|
| Roster (live era) | 22 playable heroes enumerated on the Heroes page: Squire, Apprentice, Huntress, Monk, Abyss Lord, Series EV2, Gunwitch, Lavamancer, Mystic, Dryad, Initiate, Adept, Barbarian, Mercenary, Countess, Engineer, Hunter, Aquarion, Frostweaver, Cyborg, Jester, Templar | VERIFIED enumeration — https://wiki.dungeondefenders2.com/wiki/Heroes (era-drift: launch roster was smaller — INFERRED) |
| Hero kit | "In Dungeon Defenders 2, the characters you play as are called heroes. Most heroes have 4 Abilities and 4 Defenses. The Gunwitch, Barbarian, and Frostweaver have 8 abilities and no defenses. The Mystic and Dryad have 3 abilities and 5 defenses" | VERIFIED — same page |
| Hero deck | 4 heroes per account, hot-swappable: control rows "Swap to Hero 1 … Swap to Hero 4 (F1–F4)" | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Controls |
| Level cap | 50; then endless Ascension levels: "Heroes under level 50 cannot apply any ascension points, however, upon reaching level 50, heroes can apply all ascension points that have been earned on that account." | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Ascension |
| Skill points | DD2 = account-wide Ascension points "awarded every time the player levels up and fall into one of three categories: Offense, Defense and Utility" (per-power caps 200, raisable to 999) | VERIFIED — same page |
| DD1 contrast | "At every level advancement the character gains a number of Skill points to spend on their Hero and Tower Stats" — per-hero allocation | VERIFIED (DD1) — https://dungeondefenders.fandom.com/wiki/Stats |
| Attributes | Hero gear primary/secondary: "has 1 Primary stat which is Hero Damage and 1 Secondary stat that can be Hero Health or Ability Power"; stat list = Power, Critical Chance/Damage, Health, Armor, Speed, Range (+Resistance, Tenacity) | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Stats , https://wiki.dungeondefenders2.com/wiki/Weapons |
| XP sources | kills, wave completions, daily/weekly bounties, and party scaling: "Players gain (+33%, +66%, +99%) more XP (stacks additively with other bonuses)" | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Maps |

## 3. Third-person combat

| Mechanic | DD2 reality | Evidence |
|---|---|---|
| Basic attack | "Primary Attack: LMB / RT" + "Secondary Attack: RMB / LT" (two attack styles per weapon) | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Controls ; shot types/speed/projectile-count roll on weapons — https://wiki.dungeondefenders2.com/wiki/Weapons |
| Ability bar | 4 abilities: "Ability One … Ability Four (1–4, RB+LB)"; each costs ability resource | VERIFIED — Controls |
| Ability resource | "Blue mana is used to activate Hero Abilities and Green mana is used to Build, Repair and Upgrade defenses." … "Blue Mana (also known as "Ability Mana" or "Ability Resource") … regenerates passively during the combat phase, albeit slowly." … "Blue Mana completely regenerates at the start of each new combat phase." Special pools exist per hero (e.g. Molten Energy, Wrath & Fury). | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Mana |
| Mana sharing | "Drop Ability Mana (N) / Drop All Ability Mana (Ctrl+N)" — players drop resource for others | VERIFIED — Controls |
| Targeting/lock-on | No lock-on binding exists in the fetched default Controls table (instrument: full Controls page fetched; grep 'lock' → 0). INFERRED: mouse-aim/fps-style aim, no classic lock-on. | INFERRED (absence instrumented) |
| Dodge/dash | Movement table = W/A/S/D + Jump only; no dodge/dash binding in the fetched Controls table. INFERRED: no dodge; reposition + Jump only. | INFERRED (absence instrumented) |
| Pet ability | "Pet Ability: X / RB+A" | VERIFIED — Controls |
| Inter-wave phase | Waves alternate with build phases (abilities refresh at combat-phase start — Mana quote above; green mana "given … after waves" — Mana page) | VERIFIED — Mana page |

## 4. Towers (Defenses)

| Item | Value | Evidence |
|---|---|---|
| Classes | "There are 5 types of Defenses: Towers, Blockades, Traps, Auras and Nodes." (Blockades = walls: "wide hitboxes with a lot of health"; Traps: "As health they have an certain amount of charges… each trigger removes a charge"; Auras = persistent buff/damage fields; Nodes = multi-part utility structures) | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Defenses |
| Families | Named towers enumerated per hero class on the same page, incl. Ballista, Nether Archer, Skeletal Archer (arrow-like), Tesla Coil, Rail Gun, Plasma Defense System (tesla/tech-like), Cannonball Tower, Flak Cannon, Elvish Artillery Cannon (cannon-like), Frostbite Tower, Hailstorm Tower (frost-like), Flameburst/Flamethrower (fire), plus hero-unique exotics (JellyFish, Sonic Bat, Obelisk). "Lab" family not found (grep of fetched page). | VERIFIED enumeration |
| Build cost | "They require Green Mana to be built, upgraded and repaired." Green mana comes from kills + wave completions, map-set start amount, hard cap 10,000. | VERIFIED — Defenses + https://wiki.dungeondefenders2.com/wiki/Mana |
| In-mission upgrade | Tiered upgrades bought with green mana: "Tier 1 -> 2: 50; Tier 2 -> 3: 100; Tier 3 -> 4: 150; Tier 4 -> 5: 200" (base-cost ratios). Repair: "Base Green Mana Cost * 75% * % of missing health". Sell: "Total Green Mana Cost * 75% * % of missing health". | VERIFIED — Defenses |
| Tower XP / ability tree | CONTRADICTED for DD2: no XP, no level-threshold picks; the wiki Interactions list is only Build/Upgrade/Repair/Sell. (DD1 comparison, fetched: "A single defense can be upgraded up to five times, with every level requiring more mana… the active hero must be at least level 60." — https://dungeondefenders.fandom.com/wiki/Upgrade_Defense) | VERIFIED absence + VERIFIED DD1 quote |
| Placement | Free placement with Confirm/Cancel keys ("Confirm Placement LMB / Cancel Placement RMB"); no placement-pad system in any fetched DD2 page (Defenses page grep 'pad/placement' → 0 hits). INFERRED: open placement (vs DD1-style pads — pads not found in DD2 pages either). | INFERRED (absence instrumented) |
| Defense cap | Per-map limit, e.g. The Gates of Dragonfall "Defense Units: 600" | VERIFIED — https://wiki.dungeondefenders2.com/wiki/The_Gates_of_Dragonfall |
| Tower gear/mods | "Magical Offensive/Defensive Subroutines or "Mods" for short provides passive effects and can be attached to Weapons, Armor, Relics and Rings." Slot counts: "Godly and Legendary items have 3 mod slots, Mythical and Epic items have 2 mod slots, Powerful items have 1 mod slot, and Sturdy and Worn items have no mod slots." Towers equip Relics (Medallion/Mark/Orb types). | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Mods |
| Mod transfer | "Tinkering is a process that allows for the transfer of Mods from one item to another." Cost = Defender Medals/Gems + tier Hammers + tier material. | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Tinkering |
| Shards (global tower buffs) | Shard packs as mission rewards; Hyper Shards (e.g. "Genie King's Blessing is the only way to generate Green Mana outside of mob slaying and wave completions") | VERIFIED (quote from Mana page) — https://wiki.dungeondefenders2.com/wiki/Shards (page listed; details partial) |

## 5. Missions

| Item | Value | Evidence |
|---|---|---|
| Objective structure | "Each lane starts from an enemy spawner and ends where an objective is." "There are two types of objectives - the main core (game over when destroyed) and a sub-objective (opening new lanes or disabling environmental traps when destroyed)." Cores have health bars (no separate gate HP: the core IS the health bar; lore object = Eternia Crystal). | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Maps |
| Map anatomy (example) | Gates of Dragonfall: Main Cores 1, Sub Cores 0, Ground Lanes 3, Air Lanes 2, Defense Units 600. Ground + flyer lanes; converging lanes create chokepoints. | VERIFIED — map page + Maps page |
| Wave counts | Fixed waves per match ("after all required waves has been completed" — Victory Chests). Exact per-map tables not in fetched pages (UNVERIFIED); instrumented numbers: bounty "Beat 30 waves on any survival map"; Chaos V Expedition spawns a Shield Geode "(1 per wave starting on wave 3)". | VERIFIED (quotes) / UNVERIFIED (per-map tables) |
| Boss waves | Incursions = boss-themed missions (bounty rows "Complete the Kobold Bling King Incursion" etc.); Expeditions each have "Chaos Miniboss" (e.g. Chaos X "Chaos Miniboss: Ancient Wyvern"); Onslaught mutators from floor 3. | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Expeditions , Missions page |
| Mode set | Campaign (Normal/Hard) → Adventures → Expeditions (Chaos I–X, gated by Champion Score, e.g. "Unlocked after reaching 580 champion score"); Onslaught endless: "You'll start on floor 1, begining your journey to floor 999!" (+ Survival/Incursions/Daily/Weekly). | VERIFIED — Campaign, Expeditions, Onslaught pages |
| Difficulty tiers | DD2 live: Campaign Normal|Hard + Chaos I–X tiers + Onslaught floors (enemy scaling "172.5 levels per floor"). DD1-series comparison (fetched): "Players who are new to Dungeon Defenders should first play through the Classic Campaign on Easy, Medium or Hard, then work their way up." (tiers incl. Nightmare, Ruthless). "Hell" tier found in neither fetched list. | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Campaign , https://wiki.dungeondefenders2.com/wiki/Onslaught , https://dungeondefenders.fandom.com/wiki/Difficulties |
| Multiplayer scaling | "Enemies gain, (+20%, +40%, +60%) Health, and (+10-15%, +20-30%, +30-45%) Tenacity" for 2–4 players. | VERIFIED — Maps page |

## 6. Loot

| Item | Value | Evidence |
|---|---|---|
| Rarity ladder (live era) | Worn → Sturdy → Powerful → Epic → Mythical → Legendary → Godly (ladder enumerated via mod-slot quote in §4, VERIFIED — Mods page). Live-era Victory Chest colors: "four main different rarities of chests: Powerful (Green), Epic (Blue), Mythical (Purple), and Legendary (Orange)" + red Onslaught/Terror chest. | VERIFIED — https://wiki.dungeondefenders2.com/wiki/Victory_Chests |
| Era-drift | Launch-era rarity names/colors differ (DD1 lineage: Common/Uncommon/Rare/Epic/Legendary — Quality page fetched as stub: "Quality is a property of all equipment… It may refer to the item's base quality or tier which is usually the prefix in its name."). Treat launch names as UNVERIFIED detail. | OVERSTATED-by-era note |
| Stat rolls | Items roll 1 primary + 1 secondary stat (Weapons page, §2 quote); ranged roll Attack Speed / Shot Type / Number of Projectiles; melee roll Light/Medium/Heavy weight ("Each swing deals less damage but the weapon will be swung in a rapid rate."). Relic substats random on drop; gear "stays within the level range you currently in" (Victory Chests — loot level = current Chaos tier). | VERIFIED — Weapons, Victory Chests |
| Sets | Sets exist in the DD1/Eternity line: "Much more loot variety: weapons, sets, quality levels (tiers), progression etc." — https://dungeondefenders.fandom.com/wiki/Dungeon_Defenders_Eternity . No DD2 sets page found (instrument: wiki AllPages scan) → INFERRED: no meaningful DD2 set system. | VERIFIED (DD1) / INFERRED (DD2 absence) |
| Loot channels | Victory Chests (1 per player, loot not shared); enemy drops; Unique weapons "acquired through specific locations or vendors"; Lockboxes (cosmetic, §10). | VERIFIED — Victory Chests, Weapons, Lockbox page |

## 7. Crafting / item improvement

- CONTRADICTED premise: no workshops, no legendary crafting bench in DD2 (instrument: full wiki AllPages scan → no Workshop/Crafting pages; only Crafting_Materials as drops).
- Real system (VERIFIED — https://wiki.dungeondefenders2.com/wiki/Upgrade ): "As of the Protean Shift update, gear upgrades are performed within the player's inventory. There are 5 cores to upgrading gear: Upgrading, Evolving, Advancing, Rerolling and Tinkering." Evolving/Advancing consume tier Ampoules + Gold per a Chaos-Level cost table.
- Reroll base values = stat reroll row (same page).
- Legendaries are drops (guaranteed via Legendary Victory Chests / Expeditions: multiplayer "Guarantees (+2, +4, +6) additional legendary drops in Victory Chests" — Maps page), then Evolved upward to keep them viable ("without losing its specific stat rolls" per Upgrade page mechanics).
- NPC services at hub: Blacksmith (gear), Professor Proteus "The Tinkerer" — "the genius who adapted gear to have Mods as well as the respective upgrade material (e.g Plain Leather, Plain Iron Hammer)", Seamstress (costumes), Stable Boy (pets). VERIFIED — https://wiki.dungeondefenders2.com/wiki/Non_Playable_Characters

## 8. Base building / hub

- CONTRADICTED premise (live-era): no player-built workshop rooms found in any fetched DD2 source (instrument: AllPages scan + Tavern page). Hub is a static, instanced space: "There are currently 2 Different Hubs in the game, the Private Tavern and the Heroes Market Place also known as the Town. This is where you'll spend any time not in battle to sell, buy, manage, tinker and test any gear you've found in combat." VERIFIED — https://wiki.dungeondefenders2.com/wiki/Tavern
- Hub contents (fetched): War Table (mission select), Emporium (costume/cash shop), Training Dummies (DPS test: "These fine indestructible dummies will show you how much damage a tower, or hero, does"), NPC vendors (§7), player stalls ("Player Shop Slots — You have 2 slots by default" — Gems page).
- INFERRED: earlier beta-era "base building with workshops" was a design phase that did not ship in any fetched live source; clone should implement hub-as-service-hub, not a builder.

## 9. Pets / mounts / other systems

- Pets: "Pets are creatures that help Heroes by attacking Enemies and providing Empowerment Stats." "Pets are hatched from pet eggs acquired from Enemies or Victory Chests. To hatch an egg, interact with the Stable Boy." Pet stats: attack damage, attack rate, "Empowerment Stats - Starts off as [20-55] and gains +5 per Affection level. At level 60, gives [315-350]"; pets roll rarity (Powerful→Legendary) and hatch via eggs. VERIFIED — https://wiki.dungeondefenders2.com/wiki/Pets
- Mounts: none found — instrument: Pets page word-scan 'mount' matched only the substring inside "amount". INFERRED: no mount system.
- Other fetched systems: Titles, Achievements, Mastery challenges, Champion Score (unlock currency), Flairs, Costumes, Tower Skins, Gold (gold sink), Shards (global buffs), Ancient Power (reset-to-prestige), Relics (tower gear). (Pages listed on wiki nav; depth INFERRED where not quoted.)

## 10. MONETIZATION INVENTORY (what the clone must NOT have)

Odds for any box: not published in any fetched source → UNVERIFIED odds.

| # | System | Contents / mechanic | Evidence (fetched URL + quote) |
|---|---|---|---|
| 1 | Cash currency (Gems) | Premium currency sold for real money | "Gems are a premium currency in Dungeon Defenders 2. … They can only be obtained by purchasing them with real-life currency in the in-game shop, buying certain DLC's, or Winning them through giveaways." — https://wiki.dungeondefenders2.com/wiki/Gems |
| 2 | Premium-gated heroes | Heroes sold for Gems (e.g. "All Heroes Bundle - 3,600 Gems") | "Gems can be used to purchase Heroes, Shard Packs, cosmetics and other items in the Emporium." — same URL |
| 3 | Paid storage/slots | Bag bundles, bank vaults, extra market stalls for Gems | "Best Things to Buy With Gems … Bank Vaults - 640 Gems per vault … Player Shop Slots - You have 2 slots by default." — same URL |
| 4 | Lockboxes (cosmetic loot boxes, key-gated) | Miniboss-dropped boxes; random cosmetic per class; keys via gems or grind | "Master key's can be purchased at the Treasure Pirate for ?? Gems or 500 Defender Medals. Master keys are used to open obtainable Lockboxes which can be drop from mini-bosses. Upon opening a Lockbox the player obtains a random cosmetic item of that class." — https://dungeondefenders2.fandom.com/wiki/Lockbox_Master_key ; corroboration: "It costs tokens for the key. Or you can pay to open them." / "those chests are one of the primary ways they expect the game to make money, opening them without using money is going to take a long time." — https://steamcommunity.com/app/236110/discussions/0/620712364025782570/ |
| 5 | Loot-box Defender Packs (cash shop) | 3 tiers, guaranteed-quality random items, escalating reroll costs | "There are Currently 3 tiers of defender packs in the game being the Defender Pack, Epic Pack, and the Mythical Pack. … Epic Pack will have 2 Items, 1 Epic or better quality! Mythical Pack will have 3 Items, 1 Mythical or better quality!" (reroll table 100/300/1,000) — https://wiki.dungeondefenders2.com/wiki/Defender_Packs |
| 6 | Battle pass (Defenders Pass) | Seasonal pass, purchased tiers, premium reward track, XP tasks | "Purchasable Tiers … 1,500): Unlocks the Defender Pass for the current season with access to all its premium rewards. … 1,840): Includes all benefits of the Standard Pass, plus an additional 20 levels at a discounted price." — https://wiki.dungeondefenders2.com/wiki/Defender_Pass |
| 7 | Premium pets (Gems) | Egg upgrade to premium-only rarity/abilities for Gems | "Gato and Creeper eggs can be transformed into Premium eggs via the Stable Boy by spending Gems. These pets can hatch in any rarity and can roll unique special abilities." — https://wiki.dungeondefenders2.com/wiki/Pets |
| 8 | Time gates | Daily/weekly bounty caps throttle the premium-adjacent medal currency; seasonal pass timer; grind-for-key path (thread row 4) | "Players get one new Daily Mission per day, time is based on login and can store up to 3 missions at once." — https://wiki.dungeondefenders2.com/wiki/Missions |
| 9 | XP boosters | NOT FOUND in fetched DD2 sources (instrument: wiki AllPages scan → only "Boost Aura" = a player ability). The F2P DD: Eternity line shipped cosmetic-only microtransactions: "Microtransactions were only for the new emotes. All heroes, maps, and non-legendary/super-legendary costumes are included for free." — https://dungeondefenders.fandom.com/wiki/Dungeon_Defenders_Eternity | as cited |

Clone ruling rows (design consequence): free-economy only (gold + earned medals), no paid currency, no box/keys, no battle pass, all heroes earnable, no paid slots, no timers gating progression; keep the *structural* loops these systems powered (daily bounties, seasonal content cadence, prestige) as pure gameplay.

## Open UNVERIFIED rows (next researcher pass)
1. Per-map exact wave counts and intermission structure (need map pages with wave tables).
2. Launch-era (2015) rarity names/colors vs live-era ladder; launch roster size.
3. Beta-era base-building design (Trendy forum archives not fetched successfully this session).
4. Lockbox/Defender Pack drop odds (never published in fetched sources).
5. Steam app id of the DD2 line (236110 in fetched URLs; 217030 unresolved).

# VERDICT: DONE
