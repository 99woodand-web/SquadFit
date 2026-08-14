# Biomechanics reference — for the stick-figure exercise rig

*Researched Aug 13. Grounds the motion-spec / archetype work so the stick figures
show correct form and proportions. Sources: Physiopedia ROM values, CDC joint-ROM
study, Artists Network arm anatomy, Wikipedia/Canson body-proportion canons,
NIH biomechanical squat review, and hip-hinge coaching guides.*

---

## 1. Body proportions (7.5-head canon)

Average adult = **7.5 heads tall**. Measuring in head units (head = 1):

| Landmark | Heads from top |
|---|---|
| Top of head | 0 |
| Chin | 1 |
| Chest / nipples | 2 |
| Navel | 3 |
| Hip / pubis | 4 |
| Mid-thigh | 5 |
| Knee | 6 |
| Mid-shin | 7 |
| Floor | 7.5 |

Derived ratios (the ones that matter for the rig):
- **Trunk** (shoulder → hip) ≈ **2.5 heads**
- **Leg** (hip → floor) ≈ **3.5–4 heads**
- **Arm** (shoulder → wrist) ≈ **3.5 heads**
- **Arm ≈ 0.75 × leg length**; fingertips reach mid-thigh when hanging
- **Upper arm : forearm ≈ 6 : 5** (forearm ≈ 5/6 of humerus) — already applied

### Squad Fit figure today vs. canon
- Head diameter 0.26 → figure is ≈ **6.3 heads** tall (deliberately stocky/stylised — fine)
- Leg (thigh+shin) 0.92 · torso 0.48 · arm (UA 0.38 + FA 0.31) = **0.69 → 0.75 × leg** ✅
- (Was 0.55 = 0.60 × leg before the Aug 13 fix — arms lengthened to the anatomical ratio,
  keeping 6:5 upper:forearm. Verified in the preview; squat + curl both render clean.
  **Aug 14:** 0.86 × leg read as "massive" in the seated cable row + push-up, so reduced
  to 0.75 × leg (UA 0.38, FA 0.31); push-up `sy` and plank shoulder/dir updated to match.)

---

## 2. Normal joint range of motion (degrees)

| Joint | Flexion | Extension | Notes |
|---|---|---|---|
| Shoulder | 0–**180°** | ~0–60° | 180° = arm straight overhead |
| Elbow | 0–**140–150°** | 0° | curl = elbow flexion only |
| Hip | 0–**120–140°** | ~0–30° | knee-to-chest ≈ 120° |
| Knee | 0–**130–150°** | 0° | full flexion = heel to glute |
| Ankle | dorsiflexion **15–25°** | plantarflexion ~50° | limits squat depth |

These are hard caps — the rig should never exceed them (a stick figure that
over-flexes looks wrong and teaches bad form).

---

## 3. Movement mechanics (per archetype)

**Squat** (hip drop, vertical)
- Depth: **parallel = 90–110° knee flexion**; **full/deep = 110–135°**
- "Below parallel" = hip crease below the knee. Bar path stays over mid-foot.
- Knee tracks over toes; torso stays fairly upright (high-bar).

**Hinge** (hips push BACK, horizontal)
- Deadlift / RDL / good morning: push hips **back**, NOT down — this is what separates
  hinge from squat. Minimal knee bend (soft), **neutral spine**, shoulders travel forward
  as the torso folds. Hamstrings/glutes are the prime movers.
- ROM limit: stop where the hamstrings/back would round (≈ torso ~70–80° from vertical).

**Press (push)** — elbow extends from flexed to locked; bar/dumbbell travels up. Shoulder
  flexes to 180° overhead for vertical presses.

**Pull (row/lat)** — elbow flexes while the scapula retracts; the arm pulls weight toward
  the torso. Row: elbow travels back; pulldown/pull-up: elbow travels down.

**Curl** — elbow is **pinned at the side**; ONLY the forearm rotates (~0 → 140° elbow flexion).

**Tricep extension** — elbow fixed above/behind; forearm extends from flexed → straight (0°).

**Press — horizontal (bench press)** — scapulae **retracted + depressed**; elbows ~**45–75°**
  from the torso at the chest (NOT flared to 90°); bar travels a slight curve to mid/lower
  chest; elbows stay slightly tucked.

**Press — vertical (overhead)** — bar moves in a **vertical line over mid-foot**; head pulls
  back as the bar passes the face, then comes forward "through" at lockout; finish in full
  shoulder flexion (~180°); don't arch the back.

**Pull — horizontal (row)** — **scapular retraction** drives it (depression for lat focus);
  tight elbow path pulled toward the hips = more lat, higher elbow path = upper back; torso
  hinged ~45° (bent-over row) or chest-supported.

**Pull — vertical (lat pulldown / pull-up)** — elbows travel **down toward the hips** while the
  shoulder adducts and the scapula retracts/depresses; bar to the upper chest; elbows stay close.

**Lateral raise** — arms raise out to the side to ~**90°** (shoulder height), slight forward
  lean, no shrugging; slow controlled return.

**Core** — crunch = spine flexion (lower back stays down); leg raise = hip flexion; plank /
  hollow hold = neutral-spine isometric hold (no movement, just a hold).

---

## 4. Implied changes when building the archetypes

1. ~~**Lengthen arms**~~ **done** — arm is now ≈ 0.75 × leg (UA 0.38, FA 0.31, 6:5).
2. **Clamp every joint angle to the ROM table** above — no impossible poses.
3. **Squat vs hinge must read as different** — squat drops the hip vertically;
   hinge pushes it back. They share the leg skeleton but differ in the hip path.
4. Isometric **holds** (plank, wall sit, hollow hold) = fixed pose + a subtle breathing
   bob, no angle sweep.

---

## 5. Walking gait — side-view walk cycle (farmer's carry)

*Researched Aug 14. Sources: Adobe walk-cycle guide, RebusFarm walk fundamentals,
classic animation walk-cycle references.*

**Four key poses** (per stride; the other leg is offset by half a cycle):
1. **Contact** — leading foot heel-strikes ahead, trailing foot pushes off behind;
   arms swing opposite the legs. Both feet touch the ground only at this instant.
2. **Down (recoil)** — weight shifts onto the leading foot; the support knee bends,
   the torso sinks to its lowest point.
3. **Passing** — the trailing leg swings forward past the standing leg; legs scissor;
   centre of gravity is low then begins to rise.
4. **Up (high point)** — body rises onto the toes, trailing leg reaches max forward
   extension; the highest point of the cycle. Then return to contact (roles swapped).

**Timing / spacing**
- ~2 steps per second at a normal walk (24 frames per full stride at 24 fps).
- Uneven spacing = more weight: the foot holds the flat/plant phase longer than the
  strike/toe-off extremes (ease-in/out).
- Arm swing is opposite to the legs (counterbalance) — BUT a loaded farmer's carry
  suppresses it: the arms stay down gripping the weights.
- Vertical bob: lowest at recoil (right after heel strike), highest at toe-off; keep
  it subtle.
- Foot roll per step: heel strike → flat (pause) → heel lift → toe-off → dorsiflex
  in the swing (already implemented as `footAng`).

**Horizontal travel (screen-wrap) — how the preview does it**
- The character walks **left→right** across the screen and wraps off the right edge
  back to the left, instead of marching in place.
- The body advances at a constant speed of `2 × stride` per cycle. Because the planted
  foot also travels backward `stride` relative to the body during stance, the two cancel:
  **the planted foot stays stationary on screen** (no foot-slide), and each foot swings
  forward exactly `2 × stride` to its next plant.
- Chosen numbers: stride 0.40 · lift 0.14 · hip 0.93 ± 0.02 bob · 50/50 stance/swing
  (so one foot leaves the ground the instant the other lands — the user's spec).
- Leg-length constraint: leg 0.92 (thigh 0.46 + shin 0.46) with the ground at 0.04 means
  the hip must stay ≤ ~0.95 to place a foot horizontally on the floor; hence hip 0.93
  neutral (a slightly bent-knee walk stance).
