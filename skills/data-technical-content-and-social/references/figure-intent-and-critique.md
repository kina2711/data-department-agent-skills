# What a figure is for, decided before it is drawn

Most bad diagrams are not badly drawn. They are drawn before anybody decided what they had to
show, so every element in them is defensible and the picture as a whole answers nothing. The fix
costs one sentence and it has to come first.

## The caption is the specification

Write the caption before the figure: one sentence stating what a reader should be able to conclude
from the picture. Not what it depicts — what it lets someone conclude.

`Kiến trúc pipeline` names a subject. `Đơn hàng đi qua 3 lần ghi, chỉ lần thứ 3 là idempotent`
states a conclusion, and it settles at once what the first caption left open: the 3 writes must be
distinguishable, the idempotent one marked, and anything not bearing on that distinction is
decoration.

A caption you cannot write is a figure you are not ready to draw. That is the useful failure — far
cheaper here than after an hour of layout.

## Draw only what the caption needs

Every element earns its place by supporting the conclusion. A component nobody has to see to reach
it belongs in the prose, not the picture, and the instinct to include it comes from completeness,
which is a different goal from communication.

The reverse is also worth checking: a conclusion the caption states but the picture cannot support
means the caption is a claim you are illustrating rather than showing.

## The critique pass

After drawing, and before the figure ships, run one deliberate pass in which you try to fail it.
Three questions, in this order, because a failure at each level makes the next moot.

**Can someone reach the caption's conclusion from the picture alone?** Cover the caption and look.
If the conclusion needs the caption to be visible, the figure is an illustration of a sentence
rather than evidence for it.

**Does anything in the picture support a different conclusion?** Layout carries meaning nobody chose. In `mermaid`, `d2` and `plantuml` alike, a centrally placed
box reads as important, a thick arrow as the main path, and one colour repeated across unrelated
things as a category. Those readings are made whether or
not you intended them.

**What would a reader wrongly conclude?** This is the question that catches the expensive errors.
A dashed line reads as `optional` to one person and `asynchronous` to another; an unlabelled arrow
reads as data flow to one and control flow to another. Two readings means the figure needs a legend
or a different mark.

## Iterate on the diagnosis, not the drawing

A critique that says `unclear` produces a redraw that is differently unclear. Each round names 1
specific misreading and 1 specific change, and the next round checks whether that misreading is
gone. 2 rounds is normal. Past 4, the trouble is almost always the caption rather than the drawing,
and the honest move is to split it into 2 figures.

## What this does not do

It says nothing about whether the content is correct. That belongs to
[diagram fidelity](diagram-fidelity-standard.md) and to `docs-validate-diagram-semantics`, which
check the model against the system rather than the picture against its caption. A figure can be perfectly
communicative about a system that does not work that way.
