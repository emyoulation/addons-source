---
[README](README.md) · [Advanced Topics](ADVANCED.md) · [Forum discussion](https://gramps.discourse.group/t/addon-filter-rule-requests/4148)

---

# FamilyNetworkRules

A pack of Gramps 6.0 addon filter rules returning the members and records of a person's or family's immediate families in a single filter step.

## Rules in this pack

| Rule | Namespace | Returns |
|---|---|---|
| People in the immediate families of \<anchor\> | Person | People who are members of the anchor's immediate families |
| Families in the immediate families of \<anchor\> | Family | Family records linked to the anchor's immediate families |

## Anchor selector

The first parameter in each rule is a combo box with four choices:

| Choice | Meaning |
|---|---|
| Person ID | A single person identified by Gramps ID |
| Person filter name | Everyone matched by a named Person filter |
| Family ID | Both partners of a family identified by Gramps ID |
| Family filter name | Both partners of every family matched by a named Family filter |

The second parameter is the ID or filter name corresponding to that choice.

## Include options

Seven checkboxes control which relationship types are returned. All are checked by default.

| Option | Person rule returns | Family rule returns |
|---|---|---|
| Include self | The anchor person(s) | The anchor family's partners and children |
| Include parents | Partners in the anchor's child-of families | Child-of families of each partner |
| Include siblings | Other children in the anchor's child-of families | Child-of families of each partner |
| Include spouses / partners | Partners in the anchor's spouse-of families | Other spouse-of families of each partner |
| Include children | Children in the anchor's spouse-of families | Other spouse-of families of each partner |
| Include in-laws | Parents and siblings of each spouse (one extra hop) | Child-of families of each partner's spouses |
| Include associations | People in the anchor's Associations tab | _(not applicable)_ |

## Installation

Copy the `FamilyNetworkRules/` directory into your Gramps user plugin folder (e.g. `~/.local/share/gramps/gramps60/plugins/`) and restart Gramps. The rules appear under **Family filters** in the Add Rule dialog — one in the Person category, one in the Family category.

## Usage

Open the Filter Editor (**Edit → Filter Editor…**), select the appropriate category, create a new filter, click **Add Rule**, and search for *immediate families*. Choose the anchor type from the combo box, enter the ID or filter name, then tick the relationship types to include.

## Adding a new rule to this pack

1. Write a new class in `FamilyNetworkRules.py` following the `prepare()` / `apply()` pattern — see [Advanced Topics](ADVANCED.md).
2. Add a `register(RULE, …)` block in `FamilyNetworkRules.gpr.py` with a unique `id` of the form `FamilyNetworkRules_<ClassName>`.
3. Bump `_VERSION` in `FamilyNetworkRules.gpr.py`.
4. Add tests in `test/FamilyNetworkRules_test.py`.
5. Run Black and Pylint before committing.

## Running the tests

```bash
GRAMPS_RESOURCES=. python3 -m unittest discover -p "*_test.py"
```

## Building for distribution

```bash
python3 make.py gramps60 build FamilyNetworkRules
```

## Commit message template

```
Add FamilyNetworkRules addon filter rule pack

Adds two filter rules under "Family filters":
  Person namespace: People in the immediate families of <anchor>
  Family namespace: Families in the immediate families of <anchor>

Each rule has a four-choice combo anchor selector (Person ID, Person
filter, Family ID, Family filter) and seven MyBoolean include checkboxes
(self, parents, siblings, spouses/partners, children, in-laws,
associations). MyBoolean subclasses use __init__(self, dbstate, uistate,
track) matching the EditRule widget factory signature. MyList subclass
provides the anchor type combo. In-law traversal adds one extra hop.
Associations are read from the Person record directly.

Generated-by: Claude Sonnet 4.5, Anthropic (claude-sonnet-4-5)
Co-authored-by: <Your Name> <your@email>

references 4148
```

## License

GPL-2.0-or-later. See file headers.

AI-generated code disclosure: all source files in this pack were substantially written by Claude Sonnet 4.5 (Anthropic). See the `Generated-by:` tag in each file header for the prompt summary.

---
[README](README.md) · [Advanced Topics](ADVANCED.md) · [Forum discussion](https://gramps.discourse.group/t/addon-filter-rule-requests/4148)
