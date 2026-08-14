# Retrieval and output grounding

Start from the concrete job and target output. Translate it into concepts, time/authority constraints, required personal rules and forbidden sensitivity. Retrieve in this order: authoritative fresh source records → verified Wiki notes → scoped 3_Toi context → prior outputs as examples only. Penalize stale, weak-authority, duplicate and overbroad results. Return the minimum sufficient context under the declared token budget.

A context pack states selected and omitted items, conflicts, freshness, source locators, personal-rule versions and expiry. An output manifest maps every material claim to evidence or marks it synthesis/inference/personal/unsupported. Citation existence is insufficient: verify the cited location entails the claim. When evidence conflicts or is absent, abstain or present uncertainty.

Evaluate with unseen representative queries: relevance precision, coverage, authority, freshness, citation validity, leakage/forbidden-source exclusion and abstention accuracy. Test changed wording and cross-domain ambiguity. Never improve a score by removing hard queries after a failure.
