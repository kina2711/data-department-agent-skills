# Demand-driven content at scale

Behavioural data says what people are trying to find out. A warehouse that records which products get compared, which searches return nothing useful and which pages get abandoned holds a demand map, and generating content against that map is a legitimate use of it. Generating ten thousand pages from it is also ten thousand claims nobody read.

This standard covers the second half. The first half — mining the behaviour — belongs to `product-analytics-and-experimentation`, and this work consumes its output rather than inventing its own.

## The demand signal has to be a query, not a hunch

Every generated artifact traces to the query that justified it: the cluster it came from, how many sessions it represents, over what window. A page generated because the topic seemed popular is indistinguishable, six months later, from a page generated because it was measured — except that only one of them can be re-checked when traffic does not arrive.

Record the threshold too. "Topics with at least N comparison events in the last 90 days" is a decision, and the number is the part that will be argued about when the output is reviewed.

## Volume changes what quality means

A person writing one page checks it. Nobody checks ten thousand. The controls therefore move from the artifact to the generator:

- **Every template placeholder resolves, or the artifact is not emitted.** A page reading "the best laptop for {use_case}" is worse than no page, and at volume it will happen unless emission is gated on completeness.
- **The claim must be supported by the row.** Generated text stating a product is faster needs the benchmark that says so in the same record. Text that asserts more than the data holds is the failure mode volume multiplies.
- **Sample and read.** Before publishing a batch, read a random sample end to end, including the smallest and the strangest rows. Aggregate validation passes on output no human would defend.
- **Near-duplicates are the visible symptom.** Two pages differing only in a product name are one page. Measure the overlap within the batch, not just against what exists.

## Structured markup is a claim in machine-readable form

Where generated pages carry structured data for search engines, the markup states facts — a rating, a price, a specification — and it is read by systems that will not check it. Markup must match what the page actually says and what the data actually holds. Marking up a rating the page does not display, or a price the warehouse no longer has, is a misrepresentation that scales.

## Freshness, and the pages nobody will remember

Generated content decays with its source. A page built from a benchmark table is wrong when the benchmark updates, and there is no author who notices. Bind each artifact to the source version it was generated from, re-check on a schedule, and retire rather than leave stale.

Decide the retirement rule before generating, not after the first complaint. A batch with no retirement rule is a batch someone else inherits.

## What this is not licence to do

Not to invent reviews, ratings, testimonials or experience. Not to publish under a person's byline text they did not write. Not to generate pages whose only purpose is to occupy a search result rather than answer the question that created the demand signal. The measured demand justifies addressing the topic; it does not justify the page being thin, and volume is not a defence when a single page is examined.
