# Authored prose voice

Structure can be correct while the prose is worthless. A note can carry every required heading, a valid front matter block and a filled decision table, and still open with "Trong thế giới dữ liệu ngày nay" and spend a paragraph restating its own title. This standard governs how authored explanatory prose reads — notes, lessons, deep dives, walkthroughs, dossiers, documentation. It does not govern how a task result is reported; that is the response-compression standard.

## Answer first, root first — they are not in conflict

Two rules that sound opposed apply to different parts of the same document.

The opening line answers. A reader who stops after one sentence should still know what the thing is and what it is for. No warm-up, no restatement of the question, no announcement of what the document will cover.

The body then starts from the problem, not the definition. Once the reader knows what they are looking at, the explanation earns its shape by showing what went wrong before this concept existed.

So: answer in the summary line, root in the first section. A document that buries the answer is meandering; one that opens with the problem and never states the answer is a riddle.

## Named tells, each with what to write instead

A ban list produces avoidance, not better writing. Each tell below is paired with the move that replaces it.

| Tell | Replace with |
|---|---|
| Scene-setting opener — "Trong thế giới ... ngày nay", "In today's data landscape" | The claim itself, in the first clause |
| Restating the heading as the first sentence | The first thing the heading does not already say |
| Announcing structure — "Bài viết này sẽ trình bày...", "Let's explore" | Delete; the headings already announce it |
| "Điều quan trọng cần lưu ý là", "It's worth noting that" | Delete the frame, keep the noting |
| "Không chỉ ... mà còn", "not only ... but also" | Two sentences, or one with the weaker half cut |
| Adjective triplets — "mạnh mẽ, linh hoạt và hiệu quả" | One adjective that survives a challenge, or a measurement |
| Hedge stacking — "có thể sẽ thường", "may sometimes potentially" | One hedge, placed where the uncertainty actually is |
| Closing recap of the text directly above it | The consequence, the boundary, or the next decision |
| Em dashes carrying every clause break | Vary: full stop, comma, colon, parenthesis, or restructure |
| Symmetrical rhetorical pairs — "Không phải X. Mà là Y." used as rhythm | Use once per document at most, where the contrast is the point |

The list is a checklist for the revision pass, not a set of forbidden strings. A tell used deliberately, once, where it carries meaning, is writing; the same phrase used as connective tissue is filler.

## Register, not imitation

Match the register of the corpus the piece joins — its sentence length, its level of formality, how much it assumes, whether it addresses the reader directly. Read two neighbouring documents before writing a new one.

Do not imitate a specific person's voice from samples of their speech or writing unless they asked for that and supplied the samples. Producing text in someone's voice for anyone else to read is impersonation regardless of how it was framed.

## The subtraction pass

Draft, then cut. Every paragraph earns its place by adding a fact, a distinction, a consequence or a worked step; a paragraph that only smooths the transition between two others is the transition, and it goes.

Specific passes, in order: delete the opening if the second paragraph could start the document; remove every sentence that restates the one before it; replace abstractions with the observable detail behind them; check each paragraph's first sentence carries the paragraph's actual point; cut ten to twenty percent where nothing is lost.

Word lists do not explain it. A text can contain no banned phrase and still be recognisable within a paragraph, because what gives it away is structural: it is prose written by something with no stake in being wrong.

These are the structural tells and the move that replaces each. They are here because fixing them produces better writing, which is the only reason worth fixing them.

## It commits to nothing

Generated prose hedges every claim until nothing can be held against it. *X can be a useful approach in certain contexts depending on requirements.* That sentence survives every objection because it asserts nothing.

An expert takes a position and pays for it: *use X here; below about ten thousand rows the setup cost is not worth it.* The threshold might be wrong, and being wrong in a checkable way is what makes the sentence worth reading. Hedge where the uncertainty is real, at the specific claim that is uncertain, and nowhere else.

## Its texture is uniform

Every paragraph the same length, every sentence the same shape, every section the same depth. Real writing is lumpy: a paragraph runs six sentences because the argument needed six, and the next is one line because that was the whole point.

Uniformity is the strongest signal and the easiest to fix — not by adding random variation, but by letting each point take the space it actually needs and no more.

## It shows no cost of knowing

Nothing in it suggests the writer did the thing. Expert prose carries residue: the approach that failed first, the number that surprised them, the case where the rule does not hold and why they know. *We tried the partition key on `event_date` and scans got worse, because the queries filter on `user_id`.*

You cannot fabricate this, and inventing it is the worst thing on this page — a made-up war story is a lie about experience. Either write from something you did, from a log, a decision record, a real incident, or write about the mechanism instead and leave the experience out.

## It is symmetrical

Three examples where two would do. *On one hand… on the other hand…* with both hands weighted equally. Two paragraphs of pros followed by two of cons.

Real arguments are lopsided, because reality is. Most trade-offs have a side that usually wins and a narrow condition where it does not; say which, and say the condition.

## Nothing is at stake

Generated text describes without consequence. Expert text says what happens if you get it wrong, who finds out, and when. *Get the grain wrong and every number downstream is defensible and useless, and the finance team finds it before you do.*

The consequence is often the only part the reader needs.

## It explains what it is about to say

*It is important to note that…* *This section will cover…* *Let us explore…* Meta-commentary substitutes for content and is the single easiest thing to delete. Say the thing.

## Its specificity is unfalsifiable

*Significantly improves performance.* *A wide range of use cases.* These sound concrete and cannot be checked. Real detail is checkable and often slightly odd — a specific number, a named tool at a named version, a date, a case that does not fit the pattern.

## It has no idiosyncrasy

No preference, no irritation, nothing the writer cares about more than the topic strictly warrants. A person who has done this work for years has opinions about small things and it shows. This is the hardest to add deliberately and the easiest to get honestly: write about what you actually think, and the texture arrives with it.

## Write from your own material

The reliable way to sound like yourself is to start from something that is yours — your work log, your decision records, your notes, the thing that actually happened last Tuesday. Generated prose is generic because it starts from nothing in particular.

This is why the daily work log and the knowledge vault exist elsewhere in this suite: they are the raw material that makes writing specific. Draft from them, not from a blank prompt.

## On optimising for a detector

Do not. Two reasons, and neither is about ethics.

The first is that the classifiers are unreliable in both directions. They flag human writing routinely, especially technical prose, formulaic genres and writing by non-native English speakers, and they miss generated text that has been lightly edited. A score from an unreliable classifier is not a measurement, and tuning against it is fitting to noise.

The second matters more: the moves that lower a detector score are not the moves that improve writing. Inserting random sentence-length variation, adding deliberate small errors, scattering colloquialisms — these degrade prose while chasing a number. Everything on this page makes writing better and would happen to move that number as a side effect, which is the correct relationship between the two.

If the concern is that honest work will be wrongly flagged, the durable answer is provenance rather than evasion: keep the drafts, the log entries and the sources that show how the piece was made.

## Where this stops

Fluency is not accuracy. Prose that reads well and hedges nothing can be confidently wrong, and this standard does nothing about that — sourcing, evidence and review do. Never remove a qualifier because it reads as weak when the underlying claim genuinely is qualified, and never sharpen a number, a version or a limitation to make a sentence land. A stated uncertainty is content, not filler.
