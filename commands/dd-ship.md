---
name: dd-ship
description: Package verified evidence into a release, refusing to ship any claim that has no evidence behind it.
argument-hint: "[release scope]"
disable-model-invocation: true
---

Ship stage of the harness delivery loop. Scope: $ARGUMENTS

1. Preflight every claim the release makes. A claim with no evidence reference does not ship; an unrun check is reported as **unrun**, never omitted.
2. Confirm the approval still binds: same scope, same artifact hash, inside its expiry, uses remaining. Any change to scope or hash expired the decision.
3. Confirm the runtime floor was not crossed — billing, network egress, secrets, production access, destruction outside the working tree — by reading the stop log rather than by recalling the run.
4. Run `python3 tools/prose_score.py` over any prose the release contains and act on the dimension it names. This is the last gate of the loop, deliberately: writing cannot be judged before the argument is settled, and a score raised by sprinkling in randomness is worse than the low score it replaced.
5. Assemble changelog, version and artifacts, and record what was verified against what was asserted.

**Gate.** Preflight passes or the release stops. Written is not working, and a green summary over an unrun check is a false claim.
