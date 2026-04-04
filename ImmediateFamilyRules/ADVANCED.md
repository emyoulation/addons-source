---
[README](README.md) · [Advanced Topics](ADVANCED.md) · [Forum discussion](https://gramps.discourse.group/t/addon-filter-rule-requests/4148)

---

# Advanced Topics — FamilyNetworkRules

## The prepare() / apply() performance contract

The Gramps filter engine calls `apply()` once for every object in the active category — potentially tens of thousands of calls per filter run:

> Anything that touches the database belongs in `prepare()`, not `apply()`.

`prepare()` runs **once** per filter execution. Build a `set[PersonHandle]` or `set[FamilyHandle]` there; `apply()` tests membership in O(1).

**Never store `db` on `self`.** Stash results, not the reference.

**Re-initialise in every `prepare()` call** with a fresh `set()` to prevent stale handles leaking across runs.

## The EditRule widget factory — the real signature

The filter editor's `EditRule` class processes each entry in `labels` as follows:

1. It calls `str(v)` on the entry to make a `Gtk.Label`.
2. It compares that string against a cascade of known magic strings (`"ID:"`, `"Filter name:"`, `"Place:"`, etc.) to decide which built-in widget to build.
3. If no magic string matches, it **falls through** to:

```python
else:
    t = v(self.dbstate, self.uistate, self.track)
```

This means any custom widget class in `labels` must accept exactly **three positional arguments**: `dbstate`, `uistate`, `track`. Not just `db`. The wiki example showing `__init__(self, db)` is misleading — `db` there is actually `dbstate`. The correct signature is:

```python
class _BoolParents(MyBoolean):
    def __init__(self, dbstate, uistate, track):
        MyBoolean.__init__(self, _("Include parents"))
        # dbstate/uistate/track are available if needed but ignored here
```

`MyBoolean.__init__` itself takes only `label=None` — it's a `Gtk.CheckButton` subclass. The three args from `EditRule` are accepted by our `__init__` and discarded, since checkboxes need no db access to build.

`MyList.__init__` similarly takes `(clist, clist_trans, default=0)` — no db args. Our `_AnchorType` subclass absorbs and discards the three EditRule args:

```python
class _AnchorType(MyList):
    def __init__(self, dbstate, uistate, track):
        MyList.__init__(self, _ANCHOR_KEYS, _ANCHOR_LABELS, default=0)
```

`MyList.get_text()` returns the selected entry from `clist` (the untranslated keys), so the stored parameter value is locale-independent — `"person_id"`, `"person_filter"`, `"family_id"`, or `"family_filter"` — regardless of the user's language. `MyList.set_text()` restores the selection by key when a saved filter is reloaded.

## Why two rules instead of four

Previous iterations had four rules (one per anchor type). A single rule with a `MyList` combo selector is cleaner because:

- One rule entry in the filter editor covers all four anchor modes.
- Saved filters round-trip correctly — the key string is locale-independent.
- Adding a fifth anchor mode in future means changing one rule, not adding a fifth.

## The anchor resolver pattern

`_resolve_person_anchors()` and `_resolve_family_anchors()` centralise the logic for turning the combo selection + value string into a list of handles. `prepare()` calls the resolver once, then loops over the results calling the traversal helper. This keeps `prepare()` readable and makes the resolvers independently testable.

## Registration field reference

```python
register(
    RULE,
    id="AddonDirName_ClassName",      # globally unique
    name=_("…"),
    description=_("…"),
    version="0.1.0",                  # semver — bump on every change
    gramps_target_version="6.0",
    status=UNSTABLE,                  # STABLE | UNSTABLE | EXPERIMENTAL
    fname="FamilyNetworkRules.py",
    ruleclass="ClassName",
    namespace="Person",               # or "Family", "Event", etc.
    authors=["…"],
    authors_email=["…"],
    help_url="…",
)
```

## Testing strategy

Tests use `unittest.mock.MagicMock` — no Gramps installation required.

Cover at least:

- All four anchor types resolve correctly.
- Each include flag off individually: that category is absent.
- Unknown ID or filter name: `prepare()` logs a warning, `apply()` returns `False`.
- `None` from `get_family_from_handle`: skipped gracefully.
- `prepare()` called twice: second call resets state completely.
- Anchor person not added as its own sibling.

---
[README](README.md) · [Advanced Topics](ADVANCED.md) · [Forum discussion](https://gramps.discourse.group/t/addon-filter-rule-requests/4148)
