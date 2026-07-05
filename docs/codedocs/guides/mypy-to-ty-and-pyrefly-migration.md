---
title: "Migrate From mypy To ty And pyrefly"
description: "A field-tested playbook, pitfall list, and config cheat-sheet for moving a codebase off mypy onto ty and pyrefly, written for both human and AI-agent execution."
---

This guide is not about using `fastkml`. It documents how `fastkml` itself was migrated from `mypy` to Astral's `ty` and Meta's `pyrefly`, so the same playbook can be replayed on other codebases with less trial and error. Keep it here because the next migration (human- or agent-driven) should start from findings, not from zero.

<Callout type="info">Running two checkers instead of one is deliberate, not incidental. `ty` and `pyrefly` disagree with each other and with mypy often enough that running only one gives a false sense of completeness. Budget for both, and expect them to catch different subsets of the same bugs.</Callout>

## TL;DR

1. Get a raw error-count baseline for both tools **before** touching any source. Categorize by error kind, not by file.
2. Look for one **systemic** root cause before fixing anything file-by-file. In most codebases with an optional C-extension backend (lxml, pydantic-core, orjson, etc.) there is a single architectural fix that collapses 60-90% of the noise.
3. Fix genuine bugs the tools surface (there will be some — both tools are pickier than mypy about `Optional`/union narrowing, positional-only stubs, and unpacking).
4. Bulk-suppress test-file "constructed-then-accessed-without-narrowing" noise scoped to `tests/**`, not case by case, and not by widening the rule to error kinds that could hide real bugs (`invalid-argument-type` is not `unresolved-attribute`).
5. Turn on strict presets, then promote specific rules the preset doesn't cover, and explicitly cut the ones that create disproportionate mechanical churn (ask a human before doing a 80-site `@override` sweep).
6. Verify: both tools clean, full test suite green (with **and** without optional runtime deps installed), linter clean, and the TOML re-parses.

## Phase 0 — Inventory the mypy config honestly

Before deleting `[tool.mypy]`, read what each flag actually bought you, because that's the strictness bar `ty`/`pyrefly` need to match or exceed:

| mypy setting | Rough ty/pyrefly equivalent |
|---|---|
| `disallow_any_generics` | ty `missing-type-argument = "error"` |
| `warn_redundant_casts` | ty `redundant-cast`; pyrefly `redundant-cast` (both exist, check current default level) |
| `warn_unused_ignores` | ty `unused-ignore-comment` / `unused-type-ignore-comment`; pyrefly `unused-ignore` (on by default under `strict`) |
| `warn_unreachable` | pyrefly's `strict` preset covers this; ty has no exact analog — don't assume parity, spot-check |
| `disallow_untyped_defs` | Neither tool has a literal flag for this — `ty` infers types through unannotated bodies by default (different philosophy from mypy). Don't expect a 1:1 mapping; re-derive intent instead of hunting for the same flag name. |
| Per-module `disable_error_code` overrides | pyrefly `[[tool.pyrefly.sub-config]]` + `matches` glob; ty `[[tool.ty.overrides]]` + `include` glob |

Also inventory **stale** per-module overrides — a mypy config that's been edited over years accumulates dead entries (a module path that was renamed or deleted, but the override survived). Grep for the referenced paths; don't carry dead config forward.

## Phase 1 — Install both tools and get a baseline

```bash
uv pip install ty pyrefly
ty check <src> <tests>
pyrefly check <src> <tests>
```

Immediately categorize, don't read line by line yet:

```bash
ty check <src> <tests> 2>&1 | grep -oE '^error\[[a-zA-Z-]+\]' | sort | uniq -c | sort -rn
ty check <src> <tests> 2>&1 | grep -E '^\s+-->' | sed -E 's/^\s+--> //; s/:[0-9]+:[0-9]+$//' | sort | uniq -c | sort -rn
```

The second command (errors by file) usually reveals the systemic cause immediately: a handful of files concentrate a disproportionate share of the errors, and they're usually the ones touching an optional/duck-typed dependency.

<Callout type="warn">If a partial migration already exists in the repo (CI switched over but `pyproject.toml` grew broad `ignore-missing-imports = ["*"]` / blanket `missing-attribute = "ignore"` sub-configs), treat that as a red flag, not a starting point. Broad suppressions accumulated during an in-progress migration usually mean someone hit friction and silenced it rather than fixed it. Re-run with those suppressions removed to see the real baseline before deciding what's worth keeping.</Callout>

## Phase 2 — Find the systemic root cause first

The highest-leverage move in this kind of migration is almost never "fix errors file by file." It's finding the one architectural mismatch that both checkers are tripping over identically across dozens of call sites.

**The recurring pattern**: a project supports an optional, richer backend (lxml over `xml.etree.ElementTree`, `orjson` over `json`, `ujson`, a C-accelerated regex engine, etc.) via a runtime try/except import, and defines either a `Protocol` or just relies on structural duck-typing to abstract over both. mypy tolerated this for years via `ignore_missing_imports = true`, which silently treats the untyped backend as `Any` everywhere. Neither `ty` nor `pyrefly` degrade that gracefully by default — they'll either partially resolve the untyped backend's real (but incomplete) info, or fall back to typing it against whichever branch of the try/except *does* have full stubs (usually the stdlib fallback), and then report every method/kwarg the richer backend uniquely offers as invalid.

**The fix**, applied at the import site (not scattered across every call site):

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Type-checkers see the richer backend's own stubs; the preferred
    # backend's API is treated as a superset of the fallback's.
    from lxml import etree
else:
    try:
        from lxml import etree
    except ImportError:
        import xml.etree.ElementTree as etree
```

If the project also defines its own `Protocol` to abstract over both backends (e.g. `types.py: class Element(Protocol): ...`), consider going one step further and making that Protocol **literally alias the richer backend's real type** under `TYPE_CHECKING`, falling back to the structural `Protocol` only for runtime/non-typechecking purposes:

```python
if TYPE_CHECKING:
    from lxml.etree import _Element as Element
else:
    class Element(Protocol):
        ...  # the original structural protocol, unchanged
```

This one change collapsed roughly 150 of ~240 diagnostics in the fastkml migration, because it fixed both the "backend-specific kwarg doesn't exist" class of errors *and* the "structural Protocol isn't assignable to a concrete stdlib parameter type" class in one shot (see pitfall below).

If a stub package exists for the richer backend (`lxml-stubs`, `types-ujson`, etc.), add it to your typing dev-dependencies — but read the pitfalls section before assuming it's a strict improvement for *both* checkers.

## Pitfalls (the part worth re-reading before your second migration)

### 1. `# type: ignore[code]` is not portable

Neither `ty` nor `pyrefly` parses mypy's bracketed error-code suppression the way mypy does.

- `ty` honors a **bare** `# type: ignore` (no brackets) as a blanket suppression for that line, but a bracketed `# type: ignore[some-code]` is **not** recognized as a ty-ignore at all — it's inert noise as far as ty is concerned, and the underlying error still fires.
- `pyrefly` does honor `# type: ignore[...]` by default (its `--enabled-ignores` defaults to `type,pyrefly`), so bracketed mypy comments mostly still work for pyrefly specifically.
- Both tools have their own dedicated syntax: `# ty: ignore[rule-name]` and `# pyrefly: ignore` / `# pyrefly: ignore[error-kind]`.

Verify empirically before trusting any of this — behavior can change between tool versions:

```python
def f() -> int:
    return "y"  # type: ignore[return-value]
```

Run `ty check` and `pyrefly check` against a two-line repro before deciding on a suppression strategy for the whole codebase.

**Practical rule that worked well**: keep the original `# type: ignore[code]` comment (documents intent, keeps pyrefly happy) and append `# ty: ignore[rule-name]` on the same physical line for ty. Don't strip the mypy-era comments outright; they're free documentation of *why* a line is exceptional.

### 2. pyrefly's TOML keys are snake_case even though its CLI flags are kebab-case

This is the single most time-consuming mistake to make. `pyrefly check --replace-imports-with-any 'lxml.*'` works from the CLI. Writing the "obvious" TOML equivalent:

```toml
[tool.pyrefly]
replace-imports-with-any = ["lxml.*"]   # WRONG — silently different key
```

...does not raise an error from `pyrefly check` in some code paths, but it **does** hard-fail with `pyrefly dump-config` (`unknown variant 'replace-imports-with-any'... Fatal configuration error`), and depending on invocation order this can also break `pyrefly check` itself later. The correct TOML key uses underscores:

```toml
[tool.pyrefly]
replace_imports_with_any = ["lxml.*"]
```

Meanwhile, **error-kind names** (used as dict keys under `[tool.pyrefly.errors]` or inside a `rules = {...}` table) *do* use hyphens (`missing-override-decorator`, `redundant-cast`, etc.) — matching the CLI's `--error`/`--ignore` rule-name spelling, not the config-field spelling. There is no single consistent casing convention across the whole config surface; check `pyrefly dump-config` after every config change, not just `pyrefly check`, because `check` can look clean while a nearby key is silently ignored.

<Callout type="warn">After any pyrefly config edit, run both `pyrefly dump-config` (schema/parse validation) and `pyrefly check` (behavioral validation) — one catches structural mistakes the other doesn't surface.</Callout>

### 3. pyrefly's `[[tool.pyrefly.sub-config]]` array-of-tables is fragile against interleaving

Pyrefly's per-path overrides use TOML's array-of-tables syntax:

```toml
[[tool.pyrefly.sub-config]]
matches = "tests/**/*"

[tool.pyrefly.sub-config.errors]
missing-attribute = "ignore"
```

TOML allows other, unrelated top-level tables to appear *between* `[[tool.pyrefly.sub-config]]` and its paired `[tool.pyrefly.sub-config.errors]` — the nested table still binds to the most-recently-opened array element regardless of what's interleaved. That means a `pyproject.toml` that grew organically (auto-migration tooling appending blocks near whatever happened to be at the end of the file) can end up with three sub-config blocks scattered across 100+ lines of unrelated project/tool config, and it will *still parse*. It becomes a landmine the moment someone (or an agent) deletes one `[[tool.pyrefly.sub-config]]` header without also deleting its now-orphaned `[tool.pyrefly.sub-config.errors]` block — the orphaned errors table then either binds to the wrong array element or breaks parsing entirely.

**Fix**: keep every pyrefly (and ty) config block **contiguous** in one place in the file, even if that means moving it away from wherever an automated tool first inserted it. Re-parse after every edit:

```bash
python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('OK')"
```

### 4. A `Protocol` is not assignable to a concrete class parameter

If your duck-typing abstraction is a `Protocol` (say, `types.Element`) and internal code passes `Element`-typed values into functions that are typed against the *concrete* stdlib/third-party class (`xml.etree.ElementTree.SubElement(parent: Element[Any], ...)`), both `ty` and `pyrefly` will reject it — even though the Protocol is structurally compatible at every call site. Protocol → concrete-class assignability doesn't work the way concrete → Protocol does, and a mutable/invariant attribute (`text: str` on the Protocol vs. `text: str | None` on the real class) makes it worse.

This resolves itself for free once you apply the Phase 2 fix (alias the Protocol to the real backend's type under `TYPE_CHECKING`) for internal, backend-facing code. Keep the original Protocol only for the codebase's genuinely-public, backend-agnostic API surface.

### 5. Registry/callback-style dispatch can't be narrowed at the signature level

A common pattern: a generic dispatch table stores `classes: tuple[type[object], ...]` and a matching `Protocol` requires every registered callback to accept exactly that (necessarily wide) signature, even though any *individual* callback only ever receives one concrete class at runtime. You cannot narrow an individual callback's parameter type to the concrete class it actually expects (`tuple[type[SpecificClass], ...]`) — that breaks structural assignability against the wider Protocol the dispatcher requires (parameter types are contravariant; a callback that only accepts a narrower type can't stand in for one the dispatcher will call with the wider type).

Fix at the call site inside the function body instead of the signature: `cast("tuple[type[SpecificClass], ...]", classes)`, or `cls = cast("type[SpecificClass]", classes[0])`. Keep the public signature honestly wide.

### 6. `**heterogeneous_dict` splats can't be validated against multi-parameter constructors

```python
fields = {"type_": DataType.int_, "name": "Integer"}
SimpleField(**fields)
```

Both checkers infer `fields: dict[str, DataType | str]` and then check *every* keyword argument against that whole union, rather than against each parameter's own specific type — because plain `dict[str, ...]` splatting isn't a `TypedDict`, so there's no per-key type information available. This isn't a narrowing bug or an inherent-bad-input case; it's a structural limitation of `**dict` splatting itself. Either convert the dict to a `TypedDict` (real fix, more invasive) or accept a targeted ignore comment — don't spend time trying to "fix" it any other way.

### 7. Community stub packages can behave differently per checker

If you add a community-maintained stub package (`lxml-stubs`, etc.) rather than relying on inline `py.typed` types, expect it to have its own bugs, and expect those bugs to manifest **differently per checker**. In this migration, `lxml-stubs` declares several attributes using the legacy stub syntax `tag = ...  # type: str` (pre-PEP 526). `ty` tolerates this by falling back to `Unknown` for that attribute (safe, just loses precision). `pyrefly` mis-parses it as the attribute's type being the **literal value** `Ellipsis`, then reports every subsequent use (`.strip()`, `.split()`, slicing) as an error on a nonexistent `EllipsisType` method — a wave of dozens of false positives that has nothing to do with your code.

There is no fix on your side other than working around the stub bug per-checker:

```toml
[tool.pyrefly]
# Force pyrefly to treat the whole (broken-for-pyrefly) stub package as Any,
# while `ty` still gets full value from the same installed stub package.
replace_imports_with_any = ["lxml.*"]
```

Don't assume "we added the stub package" is the end of the story — verify both tools independently after adding any third-party stub dependency, because "more type information" is not always strictly better across tools.

### 8. Fixing the root cause makes old workaround `cast()`s redundant — clean them up

Once you fix the systemic issue, re-run both tools and look specifically for `redundant-cast` warnings. Every `cast("Element", root)` that existed purely to placate mypy's `ignore_missing_imports` fallback becomes genuinely unnecessary once the real type flows through correctly, and leaving it in is now dead weight (and a `ty`/`pyrefly` warning) rather than a workaround. This is a good automatic signal that the root-cause fix actually landed.

### 9. Some "strict" rules are mechanical churn, not bug-catching — decide explicitly, don't default to on

Pyrefly's `strict` preset (and to a lesser extent `ty`'s optional rules) includes checks like `missing-override-decorator` (PEP 698 `@override`), which can flag **dozens to low-hundreds** of ordinary `__repr__`/`__init__`/method overrides in any codebase with meaningful inheritance. This is a legitimate check with real value in large team codebases (catches silently-broken overrides after a base-class rename), but adding `@override` everywhere is a large, purely mechanical diff disconnected from the actual "fix type errors" task.

Don't silently turn this on or off. Surface it explicitly (to a human reviewer, or via an explicit question if you're an agent) before deciding: disable it with a documented reason, or actually do the sweep. Either is defensible; picking silently isn't.

### 10. Test-file "narrowing noise" is real but should not become a license to blanket-suppress everything

The overwhelming majority of test-file errors in a mature test suite will be the same shape: construct an object, then immediately access/assign a field typed `X | None` or `A | B | None`, without a narrowing `assert x is not None` — because the test *knows* the value is set (it just set it three lines up) but the checker doesn't. This is legitimately safe to bulk-suppress scoped to the test tree:

```toml
[[tool.pyrefly.sub-config]]
matches = "tests/**/*"
[tool.pyrefly.sub-config.errors]
missing-attribute = "ignore"

[[tool.ty.overrides]]
include = ["tests/**"]
rules = { unresolved-attribute = "ignore", invalid-assignment = "ignore" }
```

But scope the suppressed **rule names** narrowly (`unresolved-attribute`/`missing-attribute`/the specific `invalid-assignment` shape), not broad categories like `invalid-argument-type`/`bad-argument-type` — those catch genuinely wrong types passed into calls, which do happen in test code (typos, copy-paste of the wrong fixture) and are worth keeping visible. In the fastkml migration, roughly 90% of test-file errors were narrowing noise safely bulk-suppressed, and the remaining 10% surfaced one genuine test bug (a string literal assigned where an enum member was expected) plus a batch of deliberately-invalid-input tests that just needed their ignore-comment syntax migrated (see pitfall 1).

## Phase 3 — Work file by file for what's left

After the systemic fix and the bulk test-suppression, what remains is usually a short, tractable list (tens, not hundreds, of diagnostics). For each:

1. **Read the surrounding code before deciding how to fix it.** The same `unresolved-attribute` shape can be a real narrowing gap (add `assert x is not None`, matching the style already used elsewhere in the file), a genuine latent bug (an off-by-one/empty-tuple case an unpacking `*args` call didn't guard against), or a structural dispatch limitation (pitfall 5).
2. **Prefer a real fix over a cast or ignore** wherever one exists cheaply: correcting a wrong return-type annotation (`Optional[X]` that never actually returns `None`), adding `isinstance` narrowing instead of a loose dict-dispatch, genericizing a `find`/`find_all`-style utility with `@overload` + a `TypeVar` instead of returning `object`.
3. **Use `cast()` with a one-line comment explaining *why*** when the limitation is structural (pitfalls 4-6), not because you're in a hurry.
4. Re-run the checker on just that file after each fix (`ty check path/to/file.py`) — faster feedback loop than re-running the whole tree, and it confirms the fix didn't introduce a new diagnostic in the same file.

## Phase 4 — Tighten to "maximum quality"

Once both tools report zero errors on the fixed baseline, raise the bar deliberately rather than assuming the default preset is already strict:

```toml
[tool.pyrefly]
preset = "strict"   # not "legacy" / "default" — legacy exists specifically to ease mypy migrations, it's a floor, not a target

[tool.ty.rules]
# Promote rules ty ships at warn/ignore by default; discover the full list with `ty explain rule`.
possibly-missing-attribute = "error"
possibly-missing-import = "error"
possibly-unresolved-reference = "error"
missing-type-argument = "error"
unused-ignore-comment = "error"
unused-type-ignore-comment = "error"
redundant-cast = "error"
```

Discover what's available rather than guessing:

```bash
ty explain rule                 # every rule, default level, rationale, examples
pyrefly check --help            # --preset options, --error/--warn/--ignore, --replace-imports-with-any, etc.
pyrefly dump-config             # what's actually active for this project right now
```

## Phase 5 — Verify

Don't call it done on "the type checker is quiet." Run the full loop:

```bash
ty check <src> <tests>
pyrefly check <src> <tests>
ruff check --no-fix <src> <tests>          # type-fix edits (casts, isinstance, overloads) can introduce lint issues
ruff format --check <src> <tests>
python -m pytest                            # with optional runtime deps installed
uv pip uninstall <optional-dep>             # e.g. lxml
python -m pytest -m "not <slow-marker>"     # confirm the fallback code path still works
uv pip install -e ".[typing,<optional-dep>]"
python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))"
```

The "uninstall the optional dependency and re-run tests" step matters specifically because Phase 2's fix changes how the optional backend is *typed*, not just how it's imported — if the runtime fallback logic was touched at all while chasing type errors, this is the step that catches a broken fallback path before it ships.

## Case study numbers (fastkml)

For calibration on what "a lot of noise, mostly one root cause" looks like in practice:

- Baseline: `ty` reported 237 diagnostics across source + tests; `pyrefly` reported 40 errors (with an already-too-permissive config suppressing 38 more).
- One import-site fix (Phase 2, aliasing the duck-typed `Element` Protocol and `etree` module to `lxml`'s real stubs under `TYPE_CHECKING`) collapsed `ty`'s source-only count from 47 to 13 in a single step.
- Total genuine bugs found and fixed in library source: 5 (a missed `.getroot()` call, an unguarded empty-tuple unpack in a `zip_longest` loop, a too-loose `type[object]` dispatch signature, a `Self`-in-a-list invariance issue, and one example script passing `bytes` where `str` was expected).
- Total genuine bugs found and fixed in tests: 1 (a string literal compared against an enum field).
- Final state: zero errors on `ty check` and `pyrefly check` for the CI-covered scope, with all pre-existing tests still passing, both with and without the optional `lxml` backend installed.
