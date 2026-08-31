# Technical translation into Vietnamese

The reader of a translation cannot check it. That is the whole reason they needed one, and it is why every rule here exists: the usual feedback loop, where a wrong output is noticed by the person receiving it, is missing.

## Faithful is not literal

The unit of fidelity is the claim, not the sentence. A sentence rendered word by word into Vietnamese that leaves the reader with a different belief than the source left its reader is a mistranslation, however defensible each word was.

So the check is a back-translation of meaning, not of wording: for each claim, does the Vietnamese say the same thing, with the same strength, the same hedging and the same scope? English technical prose hedges constantly — *typically*, *in most cases*, *may* — and a translation that drops those turns a qualified statement into a rule.

## Fix the terminology before translating, not after

One concept gets one Vietnamese term for the whole document, decided up front and written down. The alternative is what always happens otherwise: `partition` becomes *phân vùng* in chapter two and *phân mảnh* in chapter nine, and the reader concludes they are two things.

Decide per term whether it is translated, kept in English, or given in Vietnamese with the English in brackets on first use. Getting this wrong in the direction of over-translation is the more common failure: an audience of Vietnamese engineers reads `deadlock`, `partition key` and `idempotent` daily and does not recognise the invented Vietnamese for them. Translate the explanation; keep the term the field actually uses.

Never translate: identifiers in code, API and class names, product names, error strings the reader will search for, and citation titles.

## Register is a decision, made once

Vietnamese forces choices English does not: how the text addresses the reader, how formal it is, whether it uses *bạn* or avoids address entirely. Pick one for the document and hold it. A chapter that switches from neutral technical prose to conversational second person reads as two translators, because it usually was.

Match the source's register rather than improving it. A blunt source stays blunt.

## Numbers, units and dates are claims

Converting a unit changes what the text asserts and introduces a rounding the source did not make. Convert only when the brief says to, state the original alongside, and never convert currency without a date. Dates written `03/04` mean different days in different places; write them unambiguously.

## Do not fix the source

Where the source is wrong, outdated, or contradicts itself, translate what it says and record the problem separately. A translation that silently corrects its source produces a document that disagrees with the original and nobody can tell why. Where the source is genuinely ambiguous, pick the reading the context supports and note the other; do not resolve it by inventing precision.

Where something has no Vietnamese equivalent, a translator's note is the honest answer. Coining a term and using it as though it were established is not.

## What translationese looks like

The failure mode of machine and hurried translation is grammatical Vietnamese that no Vietnamese writer would produce: English clause order preserved, passive constructions carried over where Vietnamese would use an active or a topic-comment structure, subject pronouns inserted where Vietnamese omits them, and idioms rendered by their words.

Read the output alone, without the source, and ask whether it reads as written rather than converted. That check catches what a side-by-side comparison hides, because side by side the English is still shaping how you read the Vietnamese.

## Reuse what was approved, and re-translate only what changed

Approved sentence pairs carry across documents and keep terminology stable. When the source changes, translate the changed spans and leave the rest; a full re-translation silently churns wording the reviewer already accepted and hides the real change in the diff.

## What review has to establish

That every claim survived, that terminology matches the glossary, that the register held, and that a reader in the target audience takes the intended meaning — tested by asking one, not by asking whether the text reads smoothly. Fluent and wrong is the outcome this whole discipline exists to prevent.

A domain expert confirms the terminology. Fluency in both languages does not confer authority over what a term means in a field.
