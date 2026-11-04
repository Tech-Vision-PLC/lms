// Runtime constants for the Raven settings UI, kept out of `@/types` so that
<<<<<<< HEAD
// barrel stays type-only.

/**
 * How deep condition groups may nest in this editor. ConditionBuilder counts the
 * root group as depth 0 and offers a group while `path.length < maxDepth`, so 1
 * means only the root may gain one, a single level of nesting, and no group
 * inside a group.
 *
 * Below `raven_integration.engine.MAX_TREE_DEPTH` (4) deliberately: everything
 * authorable here saves, and a tree already stored deeper still loads and reads.
 */
export const MAX_CONDITION_DEPTH = 1
=======
// barrel stays type-only. `RULE_COMBINATORS` is the runtime form of the
// `RuleCombinator` union declared there.

export const RULE_COMBINATORS = ['Any (OR)', 'All (AND)'] as const

/** A change dropping at least this many members needs an explicit confirmation. */
export const MASS_REMOVAL_THRESHOLD = 25
>>>>>>> origin/feat/Billing
