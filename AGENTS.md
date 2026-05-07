# FDSPatch — AI Agent Context

## Build Flow

```bash
# 1. Extract all BBS → txt
python3 tools/meu_saco.py

# 2. Copy parsed .txt to src (build.py auto-grabs uasset/uexp from res/)
cp res/RED/Content/Chara/TST/Common/Data/BBS_TST.txt src/Chara/TST/Common/Data/
cp res/RED/Content/Chara/TST/Common/Data/BBS_TSTEF.txt src/Chara/TST/Common/Data/

# 3. Edit .txt in src/
#    (damage, hitbox, guard crush, blockstun, etc)

# 4. Build
python3 build.py
```

**Path diff**: `res/RED/Content/Chara/...`, `src/Chara/...`. `build.py` substitutes `src` → `build/FDSPatch/RED/Content` and pulls uasset/uexp from matching `res/` path.

**For EF files** (projectiles/effects): same flow, use `BBS_TSTEF.txt` instead of `BBS_TST.txt`.

## Character Codes
| Char  | Code |
|-------|------|
| Testament | TST |
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

## Examples

### Guard Crush on Projectile (214P / TST_Special7) ~ +20
File: `src/Chara/TST/Common/Data/BBS_TSTEF.txt`
- **CrowSpecialAtk state**: add `upon: (ENEMY_GUARD)` handler with `setGuardCrushDuration: 36` + `cmn_AtkGuardBreak`
- **UnHolyAtkFunc subroutine**: add `blockstunAmount: 12` after `cmn_AtkLv0`
- Net: 36f guard crush + 12f blockstun - ~28f remaining recovery ≈ +20

### Guard Crush on Direct Hit (236H / TST_Special2) ~ +30
File: `src/Chara/TST/Common/Data/BBS_TST.txt`
- **TST_Special2 state**: add `blockstunAmount: 12` after `cmn_hosei`, add `upon: (ENEMY_GUARD)` handler
- Net: 36f guard crush + 12f blockstun - ~18f remaining recovery ≈ +30

## Links
- [BBScript doc](https://docs.google.com/document/d/14T_P-HyA2ndJB70zzNrBTKu2RdDxQy6xwXRnuwyvczE/edit?tab=t.0#heading=h.tmz2kdhixz7m)
