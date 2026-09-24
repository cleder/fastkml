# pyuppsala as an lxml replacement — integration report

Feedback from integrating `pyuppsala` as a third, optional etree backend in
[fastkml](https://github.com/cleder/fastkml) (alongside `xml.etree.ElementTree`
and `lxml.etree`). fastkml's test suite runs its ~600 tests against each
backend it supports, so this exercised a large, real-world surface: element
construction, namespace handling, parsing (including untrusted/malformed
input), XPath, and XSD schema validation against the full OGC KML 2.2 schema
(which itself imports the Atom and xAL schemas).

**Version tested:** `pyuppsala==0.8.0`. An earlier pass was done against
`0.5.0`; this supersedes it — one issue reported against 0.5.0 (`xs:choice`
content model rejection) turned out to be a misdiagnosis on our side, corrected
below.

**Bottom line up front:** for the actual bulk of the work — building, parsing,
serializing, round-tripping, and XPath-querying XML trees — `pyuppsala.etree`
is a very high-fidelity, largely drop-in replacement for `lxml.etree`. Of
~1200 tests (stdlib + lxml + pyuppsala combined), only a handful needed
pyuppsala-specific behavior, and the fastkml-side changes needed were small and
surgical (four files, no redesign). The rough edges are concentrated in three
places: recover-mode parsing, XSD numeric validation, and namespace-prefix
resolution timing — the last one being the one I'd most want to see fixed,
since it silently produces different-but-valid output rather than erroring.

---

## Compatibility scorecard

| Area | Compatibility |
|---|---|
| Element/tree construction (`Element`, `SubElement`, attributes, text/tail) | Excellent — no changes needed |
| Parsing well-formed XML (`fromstring`, `parse`) | Excellent |
| Serialization (`tostring`, `pretty_print`, `indent`) | Excellent |
| Namespaces: Clark notation, `nsmap`, default namespace on a namespaced root | Excellent |
| Namespaces: `register_namespace()` interacting with inherited defaults | **Real gap** — see "the ugly" |
| XPath 1.0 evaluation, `getparent()`, tree navigation | Excellent |
| Exception hierarchy / naming | Excellent — genuinely nicer than lxml's in places |
| Lenient/recovering parsing (`recover=True`) | Not supported (by design) |
| XSD schema validation — structural | Good, once schemas are loaded correctly (see below) |
| XSD schema validation — numeric datatypes | **Real bug** — scientific notation |
| `lxml.etree`-specific escape hatches (`set("xmlns", …)`, `.assert_()`) | Gaps, each with a clean workaround |

---

## The good

Worked correctly, with zero behavioral differences from lxml, on the first try:

- `fromstring`, `fromstring(bytes)` (including honoring/overriding a declared
  encoding), `tostring`, `parse`, `Element`, `SubElement`, `find`, `findall`,
  `iter`, `itertext`, `getparent()`, `getnext()`/`getprevious()`.
- `tostring(pretty_print=True)`, `indent()`.
- `xpath()` evaluation, including attribute-axis and text-node results,
  `XPathEvalError`.
- Clark-notation + `nsmap={None: uri}` construction: a root element built this
  way serializes with a clean, unprefixed default namespace, identical to
  lxml — `<kml xmlns="..."/>`, not `<ns0:kml xmlns:ns0="..."/>`.
- `XMLSchema(file=...)` correctly resolves `xsd:import`/`xsd:include`
  `schemaLocation`s relative to the schema file's own directory — validated
  against the real OGC KML 2.2 schema, which imports both the Atom and xAL
  (address) schemas. This "just worked" once we passed a file path (see the
  gotcha under "the bad").
- The exception hierarchy is thoughtfully designed and well documented inline
  — `XMLSyntaxError`/`ParseError`/`DocumentInvalid`/`XMLSchemaParseError` map
  cleanly onto lxml's names, and several docstrings explain *why* a given
  choice diverges from lxml (e.g. the XML-1.0-illegal-character stripping
  behavior, or the DOM-safety rationale for rejecting certain inputs). This
  made debugging divergences much faster than it would have been with an
  undocumented C extension.
- `error_log`/`DocumentInvalid.error_log` as a list of objects with
  `.message` (matches lxml's iteration-friendly `_ErrorLog` shape).

## The bad

Documented, sensible-by-design limitations that nonetheless cost a migrator
some work:

1. **`XMLParser(recover=True)` raises `NotImplementedError`.** A deliberate
   security choice (no lenient/recovering parser), which is fine — but it's a
   hard failure at parser-construction time rather than something a caller can
   detect and route around cheaply. We ended up with:

   ```python
   try:
       parser = etree.XMLParser(huge_tree=True, recover=True)
   except NotImplementedError:
       parser = etree.XMLParser(huge_tree=True)
   ```

   A `parser.supports("recover")` capability check, or an
   `UnsupportedFeatureWarning` instead of an exception (so the parser is still
   usable, just without that leniency), would make this less of a branch to
   maintain. Practically, this also means any XML with e.g. an undeclared
   namespace prefix now fails at **parse time** with `XMLSyntaxError` instead
   of parsing successfully and only failing **schema validation** later with
   `AssertionError`/`DocumentInvalid` — a behavior difference visible to end
   users of anything built on top of pyuppsala, not just an internal detail.

2. **`XMLSchema` has no `assert_()` alias.** lxml's `XMLSchema` provides both
   `assertValid()` (raises `DocumentInvalid`) and `assert_()` (raises
   `AssertionError`, and is what a lot of lxml code in the wild actually
   calls). Adding `assert_ = assertValid`, or having `assertValid` raise
   `AssertionError` directly, would remove a common workaround:

   ```python
   if hasattr(schema_parser, "assert_"):
       schema_parser.assert_(element)
   else:
       try:
           schema_parser.assertValid(element)
       except Exception as e:
           raise AssertionError(str(e)) from e
   ```

3. **Validation error-log entries have no `.path`.** lxml's `_LogEntry` (from
   `error_log`) exposes `.path`, an XPath-ish pointer to the failing node,
   which callers commonly use to locate the failure in the source tree for
   error reporting. pyuppsala's `ValidationError` only exposes
   `message`/`line`/`column`. `line`/`column` are useful too, but for an
   already-parsed-and-mutated in-memory tree (rather than freshly re-reading
   the source text), `.path` is what lets a caller highlight *which element*
   failed. Not a bug, just a smaller error-log entry shape than lxml's.

## The ugly

Real bugs, or lxml-compatible-looking APIs that silently do something
different rather than erroring — these are the ones worth prioritizing,
because they don't fail loudly:

1. **`register_namespace()` forces a prefix onto every element built in that
   namespace, even when an ancestor already declares it as the (unprefixed)
   default namespace.** This is the most consequential gap we found, because
   it breaks a very common lxml idiom: register global prefixes once (for a
   nice, deterministic serialization), then build a tree where the root
   declares its own namespace as the default (`nsmap={None: uri}`) so children
   serialize unprefixed. Under lxml:

   ```python
   etree.register_namespace("kml", "http://www.opengis.net/kml/2.2")
   root = etree.Element(
       "{http://www.opengis.net/kml/2.2}kml",
       nsmap={None: "http://www.opengis.net/kml/2.2"},
   )
   etree.SubElement(root, "{http://www.opengis.net/kml/2.2}Document")
   # <kml xmlns="..."><Document/></kml>   — child inherits the default ns
   ```

   Under pyuppsala 0.8.0, the *identical* code produces:

   ```
   <kml xmlns="..."><kml:Document xmlns:kml="..."/></kml>
   ```

   The child gets an explicit `kml:` prefix and its own redundant `xmlns:kml=`
   declaration. Root cause: `_prefix_for_ns()` resolves a tag's prefix from
   the global namespace registry *at element-construction time*
   (`_build_element`, before the element is even attached to a parent), so it
   never gets a chance to see that an ancestor already declares the same URI
   as the default. By the time `_finalize_element_ns()` runs its "reuse an
   in-scope declaration" pass (which does correctly walk ancestors), the
   element's prefix has already been baked in and — worse — a redundant
   self-declaration has already been added, so even manually resetting
   `element.tag = element.tag` afterward doesn't fix it (the self-declaration
   is itself now "in scope" and wins the lookup). We could find no supported,
   public-API way to unwind this once it's happened.

   This isn't wrong XML — it's valid, and it round-trips consistently — but it
   means **any application that has ever called `register_namespace()` for a
   namespace it also uses as a default namespace somewhere will get visibly
   different (though semantically equivalent) output than lxml**, with no
   warning. It cost us the most investigation time of anything in this list,
   because the symptom (extra prefixes deep in a tree) looked nothing like the
   cause (a `register_namespace()` call made possibly hundreds of lines away,
   at a different layer). We worked around it in fastkml by simply not
   registering a prefix for our "would be a default namespace" case, at the
   cost of losing the friendly prefix for that one namespace when it's used
   standalone (outside of a tree that establishes it as default).

2. **`Element.set("xmlns", uri)` serializes as a literal `xmlns_="..."`
   attribute instead of a namespace declaration.**

   ```python
   el = etree.Element("kml")
   el.set("xmlns", "http://www.opengis.net/kml/2.2")
   etree.tostring(el)
   # b'<kml xmlns_="http://www.opengis.net/kml/2.2"/>'   — silently wrong
   ```

   lxml special-cases `"xmlns"` in `.set()` as a default-namespace
   declaration. `set("xmlns", ...)` is a real pattern in lxml code in the
   wild (it's how you'd naively try to add a default namespace to an
   already-unnamespaced element), and pyuppsala accepts it silently and
   writes nonsense. Either honoring it like lxml, or raising a clear
   `ValueError` ("use nsmap to declare namespaces"), would turn this from a
   silent-wrong-output bug into a fail-fast one.

3. **`nsmap={None: uri}` on an element that itself has *no* namespace produces
   `xmlns=""`, losing the URI entirely.**

   ```python
   etree.Element("kml", nsmap={None: "http://www.opengis.net/kml/2.2"})
   # <kml xmlns=""/>   — URI silently dropped
   ```

   This only works when the element's own tag is *also* in that namespace
   (Clark notation, e.g. `"{uri}kml"`). We needed "an unnamespaced element
   that nonetheless declares a default namespace for the record" for one edge
   case (`KML(ns="")` in fastkml — an intentionally-unprefixed, non-namespaced
   document), and neither this nor the `set("xmlns", ...)` route above could
   produce it; there doesn't appear to be a way to get `<kml xmlns="uri"/>`
   for an unnamespaced `kml` element through the public API at all.

4. **A schema built from an already-parsed tree object
   (`XMLSchema(some_tree)`) silently loses the ability to resolve relative
   `xsd:import`/`xsd:include`.** Not something we'd call a bug exactly — more
   a sharp migration edge, and worth documenting prominently since the failure
   mode is confusing. lxml's `XMLSchema` accepts either a parsed tree or a
   `file=` path/file-like, and resolves relative imports correctly either way
   because it tracks the source URL on the `_ElementTree`. pyuppsala's
   `XMLSchema.__init__`, when given `etree=some_tree`, re-serializes it to a
   string (`tostring(etree, encoding="unicode")`) and parses *that* — which
   necessarily discards any notion of "what directory did this come from,"
   so relative `schemaLocation`s in `xsd:import`/`xsd:include` can't resolve.
   The failure surfaces much later and far from the cause: validating a real,
   valid document produces `Element reference '{...}author' not found` /
   `... not found` errors that look like a validator bug, not a "you
   constructed the schema the wrong way" issue. It took a side-by-side
   `file=` vs `etree=` comparison to find. Once we switched to always passing
   `file=<path>`, this fully resolved (and the "`xs:choice` content model
   rejection" we originally reported against 0.5.0 for the same reason — it
   wasn't a content-model bug at all, it was this). Suggestion: either make
   `XMLSchema(etree=...)` preserve/accept an optional `base_path` explicitly
   (so it's an opt-in rather than a silent loss), or have it raise/warn when
   it encounters an unresolvable relative import instead of surfacing as
   "element reference not found" deep in validation.

5. **XSD `xs:double` `minInclusive`/`maxInclusive` validation rejects
   in-range values serialized in scientific notation** — a genuine numeric
   bug, not a migration gotcha:

   ```python
   # schema: xs:double restricted to [-180.0, 180.0]
   # document: <north>4.9e-05</north>
   schema.assertValid(doc)
   # ValidationError: Value '4.9e-05' exceeds maxInclusive 180.0
   ```

   `4.9e-05` is `0.000049`, nowhere near `180.0`. This reproduces for any
   scientific-notation value we tried, including deep-underflow ones like
   `7.35697029884704e-132`. It looks like the numeric comparison is done
   lexicographically on the string form, or the exponent isn't being parsed
   at all, rather than parsing to a float/decimal first. This is a real
   correctness bug (not a lxml-compatibility gap) and the one most likely to
   silently bite real users, since `repr(float)` in Python routinely produces
   scientific notation for small magnitudes — any application validating
   XML containing small floats (percentages, ratios, coordinates near zero,
   etc.) against an `xs:double`-typed element with range constraints will hit
   this. We worked around it in our property-based (hypothesis) test suite by
   stubbing out schema validation for generated documents, and rely on our
   lxml test variants for schema-validation coverage instead.

---

## Suggested priority, if useful

1. Fix the scientific-notation `xs:double` range bug (#5 under "the ugly") —
   correctness bug, not a compat gap, and easy to hit by accident.
2. Fix or at least loudly flag the `register_namespace()` /
   default-namespace-inheritance interaction (#1) — the one that produces
   silently-different-but-valid output, which is the worst kind of bug for a
   drop-in-replacement library to have.
3. Either honor or reject `set("xmlns", ...)` (#2) — currently silently wrong.
4. `assert_()` alias and `.path` on log entries are cheap, low-risk additions
   that would remove two small but recurring workarounds.
5. `XMLSchema(etree=...)`'s import-resolution loss (#4) is probably fine to
   leave as documented behavior, but the failure mode should be much louder.

Happy to share the fastkml-side workarounds/tests in more detail, or test
against a patched build if useful.
