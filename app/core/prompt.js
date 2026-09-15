'use strict';

/* Composing a preset job's prompt from its parameters.
 *
 * This was inside the renderer, wedged between two functions that build DOM, so the only way to
 * ask "what prompt would these values produce" was to open the app and look. It is pure text
 * work, and the CLI needs the same answer, so it lives here and both doors call it.
 *
 * The template is a list of parts. A plain string is always included; an object with `neu` is
 * included only when that parameter was filled, which keeps optional sentences out of the prompt
 * instead of leaving empty placeholders inside it.
 */

// An unfilled slot collapsing to nothing leaves "cho , mức ." — a sentence that reads as broken
// rather than as incomplete. With labels the slot stays legible for a preview; without them it
// resolves, because a run is blocked until every required slot is set.
function fill(text, values, labels) {
  return String(text).replace(/\{([a-z0-9_]+)\}/g, (_m, key) => {
    const value = String(values[key] || '').trim();
    if (value) return value;
    return labels ? `⟨${labels.get(key) || key}⟩` : '';
  });
}

function composePrompt(job, values, labels) {
  const parts = [];
  for (const part of job.mau || []) {
    if (typeof part === 'string') {
      parts.push(fill(part, values, labels));
      continue;
    }
    const condition = String(part.neu || '').trim();
    if (condition && !String(values[condition] || '').trim()) continue;
    parts.push(fill(part.text || '', values, labels));
  }
  // A user-typed value rarely ends in punctuation, and two fragments joined by a space read as
  // one run-on sentence. Terminate each part rather than asking every template author to remember.
  return parts
    .map((p) => p.trim())
    .filter(Boolean)
    .map((p) => (/[.!?:;]$/.test(p) ? p : `${p}.`))
    .join(' ')
    .replace(/[ \t]+/g, ' ')
    .trim();
}

function missingRequired(job, values) {
  return (job.thong_so || [])
    .filter((p) => p.bat_buoc && !String(values[p.key] || '').trim())
    .map((p) => p.nhan);
}

module.exports = { fill, composePrompt, missingRequired };
