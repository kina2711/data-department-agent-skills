# Migration and tool interoperability

Use export-first, non-destructive migration. Inventory databases/pages/files/rows, attachments, backlinks, formulas, comments, permissions and canonical ownership before mapping. Keep raw exports under `1_Nguon/imports/<tool>/<snapshot>` with hashes; transform into portable Markdown/YAML/JSON in a separate step.

- Notion/Lark: preserve page/database IDs, hierarchy, properties, attachments and link targets; flag unsupported blocks and permission gaps.
- Sheets: preserve sheet/range identity, formulas versus displayed values, locale/timezone and automation dependencies; do not turn every row into a prose note.
- Drive/files: preserve paths, MIME types, modified times, duplicates and sharing/sensitivity metadata.
- Obsidian/local vault: use relative links, stable frontmatter IDs and portable attachments; plugins are optional adapters, not canonical dependencies.

Run counts, hash/sample comparisons, broken-link checks and representative retrieval before cutover. Keep rollback instructions and do not delete the source tool merely because export succeeded.
