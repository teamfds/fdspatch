# FDSPatch — AI Agent Context

## Build Flow

```bash
# 1. Extract all BBS → txt
python3 tools/meu_saco.py

# 2. Copy assets to src (strip RED/Content/ prefix)
cp res/RED/Content/Chara/TST/Common/Data/BBS_TST.uasset src/Chara/TST/Common/Data/
cp res/RED/Content/Chara/TST/Common/Data/BBS_TST.uexp   src/Chara/TST/Common/Data/
cp build/parsed_bbs/RED/Content/Chara/TST/Common/Data/BBS_TST.txt src/Chara/TST/Common/Data/

# 3. Edit .txt in src/
#    (damage, hitbox, guard crush, blockstun, etc)

# 4. Build
python3 build.py
```

**Path diff**: `res/` = `RED/Content/Chara/...`, `src/` = `Chara/...`. `build.py` replaces `src` → `build/FDSPatch/RED/Content`.

**For EF files** (projectiles/effects): same flow, use `BBS_TSTEF` instead.

## Character Codes
| Char  | Code |
|-------|------|
| Testment | TST |
| (Main BBS = BBS_TST, Effect BBS = BBS_TSTEF) |

## BBS File Types
- `BBS_{CODE}.txt` — main character logic (moves, normals, specials)
- `BBS_{CODE}EF.txt` — effects, projectiles, visual objects
- `COL_{CODE}` — collision data

## BBScript Patterns

### Guard Crush
Must be inside `upon: (IMMEDIATE)` of the state:
```
upon: (ENEMY_GUARD)
  clearRegisteredUponCode: (ENEMY_GUARD)
  setGuardCrushDuration: 36
  callSubroutine: s32'cmn_AtkGuardBreak'
endUpon:
```
`guardCrush: 1` alone does NOT work — needs `cmn_AtkGuardBreak` + duration.

### Damage
```
damage: Val(31)
```

### Frame Advantage
```
blockstunAmount: X    ; frames of blockstun on opponent
```
Set after `cmn_AtkLv0`-`cmn_AtkLv4` to override default blockstun.

### Startup (Frame Animation)
Sprites before `hit:` define startup:
```
sprite: s32'name', 2
sprite: s32'name', 2
sprite: s32'name', 1
hit:                              ← hitbox active here
```

### Movement
```
physicsXImpulse: 0, -25000        ; negative = backward
physicsYImpulse: 0, 40000
velocityXPercentEachFrame: 83
setGravity: 2100
```

### Button Mapping
| Code | Button |
|------|--------|
| A | P (Punch) |
| B | K (Kick) |
| C | S (Slash) |
| D | H (Heavy Slash) |
| E | D (Dust) |
| F | Switch/Taunt |

### Common Subroutines
| Subroutine | Effect |
|---|---|
| `cmn_AtkLv0`-`cmn_AtkLv4` | Attack level (damage, hitstop, blockstun) |
| `cmn_hosei` | Damage scaling adjustment |
| `cmn_countertype_middle` | Counter type (mid) |
| `cmn_AtkGuardBreak` | Guard crush setup |
| `cmnAddTensionGG` | Add tension gauge |
| `cmnNandemoCancel` | Cancel flag |
| `cmn_NoBlend` | No animation blending |
| `cmn_screenshake` | Screenshake on hit |
| `cmn_motionblur_ex` | Motion blur effect |

## Mod: Testment 214P (TST_Special7) — Guard Crush +20

### Changes in `src/Chara/TST/Common/Data/BBS_TSTEF.txt`:

**CrowSpecialAtk state** (around line 1299):
- Added `upon: (ENEMY_GUARD)` handler with `setGuardCrushDuration: 36` + `cmn_AtkGuardBreak`

**UnHolyAtkFunc subroutine** (around line 1412):
- Added `blockstunAmount: 12` after `cmn_AtkLv0` (default 9 → 12, combined with 36f guard crush ≈ +20 total)

### Note
Guard crush and blockstun may stack additively. 36f guard crush + 12f blockstun = 48f total lockout. TST_Special7 has ~28f remaining recovery after crow hitbox activates → net ~+20.

## Links
- [BBScript doc](https://docs.google.com/document/d/14T_P-HyA2ndJB70zzNrBTKu2RdDxQy6xwXRnuwyvczE/edit?tab=t.0#heading=h.tmz2kdhixz7m)
