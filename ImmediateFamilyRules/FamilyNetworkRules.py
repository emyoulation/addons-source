#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Claude Sonnet 4.5, Anthropic
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Generated-by: Claude Sonnet 4.5, Anthropic (claude-sonnet-4-5), 2026
# Prompts: "Fix MyBoolean subclass signature to match EditRule fall-through:
#   __init__(self, dbstate, uistate, track); use MyList for a 4-choice anchor
#   type selector (Person ID / Person filter / Family ID / Family filter) so
#   a single rule covers all variants; keep MyBoolean subclasses for the seven
#   include checkboxes; implement _collect_* helpers for Person and Family
#   anchor traversal; two rules total — one Person-output, one Family-output —
#   each with MyList anchor selector plus seven MyBoolean include flags."

# ------------------------
# Python modules
# ------------------------
import logging

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.filters.rules import Rule
from gramps.gen.lib import Family, Person
from gramps.gen.types import FamilyHandle, PersonHandle
from gramps.gui.editors.filtereditor import MyBoolean, MyList

# ------------------------
# Gramps specific
# ------------------------
# (local imports from this addon go here)

LOG = logging.getLogger(__name__)

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

# ---------------------------------------------------------------------------
# Anchor type selector — stored as an index into these lists
# ---------------------------------------------------------------------------
_ANCHOR_KEYS = [
    "person_id",
    "person_filter",
    "family_id",
    "family_filter",
]
_ANCHOR_LABELS = [
    _("Person ID"),
    _("Person filter name"),
    _("Family ID"),
    _("Family filter name"),
]

# Parameter indices
_P_ANCHOR_TYPE = 0   # MyList  — which of the 4 anchor modes
_P_ANCHOR_VAL = 1    # MyEntry — the ID or filter name
_P_SELF = 2
_P_PARENTS = 3
_P_SIBLINGS = 4
_P_SPOUSES = 5
_P_CHILDREN = 6
_P_INLAWS = 7
_P_ASSOC = 8


# ---------------------------------------------------------------------------
# MyBoolean subclasses
#
# The EditRule fall-through calls: t = v(self.dbstate, self.uistate, self.track)
# So every custom widget class must accept (dbstate, uistate, track).
# MyBoolean.__init__ takes only (label=None) — no db args — so subclasses
# accept and discard the three positional args from EditRule.
# ---------------------------------------------------------------------------


class _BoolSelf(MyBoolean):
    """Checkbox: include the anchor person/family themselves."""

    def __init__(self, dbstate: object, uistate: object, track: list) -> None:
        MyBoolean.__init__(self, _("Include self"))


class _BoolParents(MyBoolean):
    """Checkbox: include parents."""

    def __init__(self, dbstate: object, uistate: object, track: list) -> None:
        MyBoolean.__init__(self, _("Include parents"))


class _BoolSiblings(MyBoolean):
    """Checkbox: include siblings."""

    def __init__(self, dbstate: object, uistate: object, track: list) -> None:
        MyBoolean.__init__(self, _("Include siblings"))


class _BoolSpouses(MyBoolean):
    """Checkbox: include spouses and partners."""

    def __init__(self, dbstate: object, uistate: object, track: list) -> None:
        MyBoolean.__init__(self, _("Include spouses / partners"))


class _BoolChildren(MyBoolean):
    """Checkbox: include children."""

    def __init__(self, dbstate: object, uistate: object, track: list) -> None:
        MyBoolean.__init__(self, _("Include children"))


class _BoolInlaws(MyBoolean):
    """Checkbox: include in-laws (parents and siblings of each spouse)."""

    def __init__(self, dbstate: object, uistate: object, track: list) -> None:
        MyBoolean.__init__(self, _("Include in-laws"))


class _BoolAssoc(MyBoolean):
    """Checkbox: include people in the anchor's Associations tab."""

    def __init__(self, dbstate: object, uistate: object, track: list) -> None:
        MyBoolean.__init__(self, _("Include associations"))


# ---------------------------------------------------------------------------
# AnchorType — MyList subclass for the 4-choice anchor selector
#
# MyList.__init__(self, clist, clist_trans, default=0) takes no db args,
# so the subclass absorbs and discards dbstate/uistate/track.
# ---------------------------------------------------------------------------


class _AnchorType(MyList):
    """
    Combo box for selecting which kind of anchor the rule uses.

    Choices: Person ID, Person filter name, Family ID, Family filter name.
    """

    def __init__(self, dbstate: object, uistate: object, track: list) -> None:
        MyList.__init__(self, _ANCHOR_KEYS, _ANCHOR_LABELS, default=0)


# Shared labels tuple used by both rule classes.
# EditRule reads this as: label-string → Gtk.Label; class → instantiate with
# (dbstate, uistate, track).  Plain strings produce a Gtk.Label on the left
# and the matching widget on the right.  A class in this position means the
# label column is *also* the widget — no separate Gtk.Label is shown.
#
# For our anchor value field we use the magic string "ID:" which EditRule
# already handles by building a MyID widget with a Select button.  This
# gives us the person-ID entry + Select button for free when Person ID mode
# is chosen, and a plain text entry in the other modes (the user types the
# filter name or family ID directly).  A future enhancement could swap this
# widget dynamically based on the AnchorType selection.

_RULE_LABELS = [
    _AnchorType,       # combo: which anchor type
    _("ID:"),          # text entry / Select button for the anchor value
    _BoolSelf,
    _BoolParents,
    _BoolSiblings,
    _BoolSpouses,
    _BoolChildren,
    _BoolInlaws,
    _BoolAssoc,
]


# ---------------------------------------------------------------------------
#
# _IncludeFlags
#
# ---------------------------------------------------------------------------
class _IncludeFlags:
    """
    Parse a rule's ``list[]`` checkbox block into boolean include flags.

    :param params: ``self.list`` slice starting at ``_P_SELF``.
    """

    def __init__(self, params: list[str]) -> None:
        def _b(i: int) -> bool:
            try:
                return params[i] == "1"
            except IndexError:
                return True  # default to included for forward compatibility

        self.include_self: bool = _b(0)
        self.include_parents: bool = _b(1)
        self.include_siblings: bool = _b(2)
        self.include_spouses: bool = _b(3)
        self.include_children: bool = _b(4)
        self.include_inlaws: bool = _b(5)
        self.include_assoc: bool = _b(6)


# ---------------------------------------------------------------------------
#
# _collect_from_person  — build Person handle set from one anchor Person
#
# ---------------------------------------------------------------------------
def _collect_from_person(
    db: object,
    anchor: Person,
    match_handles: set[PersonHandle],
    flags: _IncludeFlags,
) -> None:
    """
    Traverse the immediate family graph of a Person anchor and add matching
    Person handles to ``match_handles``.

    Pass 1 — child-of families: parents and siblings.
    Pass 2 — spouse-of families: spouses/partners and children.
    Pass 3 — in-law families: parents and siblings of each spouse.
    Pass 4 — associations: read directly from the Person record.

    :param db: The Gramps database object.
    :param anchor: The anchor Person.
    :param match_handles: Mutable set receiving matching handles.
    :param flags: Which relationship categories to include.
    """
    anchor_handle: PersonHandle = anchor.get_handle()

    if flags.include_self:
        match_handles.add(anchor_handle)

    # Pass 1: child-of families
    for fam_handle in anchor.get_parent_family_handle_list():
        family = db.get_family_from_handle(fam_handle)
        if family is None:
            continue
        if flags.include_parents:
            for h in (family.get_father_handle(), family.get_mother_handle()):
                if h:
                    match_handles.add(h)
        if flags.include_siblings:
            for ref in family.get_child_ref_list():
                if ref.ref != anchor_handle:
                    match_handles.add(ref.ref)

    # Pass 2: spouse-of families
    spouse_handles: list[PersonHandle] = []
    for fam_handle in anchor.get_family_handle_list():
        family = db.get_family_from_handle(fam_handle)
        if family is None:
            continue
        for h in (family.get_father_handle(), family.get_mother_handle()):
            if h and h != anchor_handle:
                if flags.include_spouses:
                    match_handles.add(h)
                if flags.include_inlaws:
                    spouse_handles.append(h)
        if flags.include_children:
            for ref in family.get_child_ref_list():
                match_handles.add(ref.ref)

    # Pass 3: in-law families
    if flags.include_inlaws:
        for spouse_handle in spouse_handles:
            spouse = db.get_person_from_handle(spouse_handle)
            if spouse is None:
                continue
            for fam_handle in spouse.get_parent_family_handle_list():
                family = db.get_family_from_handle(fam_handle)
                if family is None:
                    continue
                for h in (
                    family.get_father_handle(),
                    family.get_mother_handle(),
                ):
                    if h and h != anchor_handle:
                        match_handles.add(h)
                for ref in family.get_child_ref_list():
                    if ref.ref != anchor_handle:
                        match_handles.add(ref.ref)

    # Pass 4: associations
    if flags.include_assoc:
        for ref in anchor.get_person_ref_list():
            match_handles.add(ref.ref)


# ---------------------------------------------------------------------------
#
# _collect_from_family  — build Person handle set from one anchor Family
#
# ---------------------------------------------------------------------------
def _collect_from_family(
    db: object,
    anchor_family: Family,
    match_handles: set[PersonHandle],
    flags: _IncludeFlags,
) -> None:
    """
    Expand an anchor Family into matching Person handles.

    The anchor Family's partners become the "self" level.  The rule then
    traverses outward from each partner using ``_collect_from_person``,
    with the include flags applied.  This means:

    - **self**: both partners of the anchor family.
    - **parents**: parents of each partner (their families of origin).
    - **siblings**: siblings of each partner.
    - **spouses**: other partners of each partner (from other families).
    - **children**: all children of the anchor family *and* any other
      families of each partner.
    - **in-laws**: parents and siblings of each partner's spouses.
    - **associations**: associations of each partner.

    :param db: The Gramps database object.
    :param anchor_family: The anchor Family object.
    :param match_handles: Mutable set receiving matching handles.
    :param flags: Which relationship categories to include.
    """
    # Always collect the anchor family's own children regardless of flags,
    # since the family IS the anchor — analogous to "self" at family level.
    if flags.include_self or flags.include_children:
        for ref in anchor_family.get_child_ref_list():
            match_handles.add(ref.ref)

    for partner_handle in (
        anchor_family.get_father_handle(),
        anchor_family.get_mother_handle(),
    ):
        if not partner_handle:
            continue
        if flags.include_self:
            match_handles.add(partner_handle)
        partner = db.get_person_from_handle(partner_handle)
        if partner is None:
            continue
        # Reuse person traversal for all outward relationships,
        # but suppress "self" to avoid double-adding partners.
        outward_flags = _IncludeFlags(
            [
                "0",  # self already handled above
                "1" if flags.include_parents else "0",
                "1" if flags.include_siblings else "0",
                "1" if flags.include_spouses else "0",
                "1" if flags.include_children else "0",
                "1" if flags.include_inlaws else "0",
                "1" if flags.include_assoc else "0",
            ]
        )
        _collect_from_person(db, partner, match_handles, outward_flags)


# ---------------------------------------------------------------------------
#
# _resolve_anchors  — resolve the anchor parameter to a list of Person handles
#
# ---------------------------------------------------------------------------
def _resolve_person_anchors(
    db: object,
    anchor_type: str,
    anchor_val: str,
    rule_name: str,
) -> list[PersonHandle]:
    """
    Resolve the anchor selector to a list of Person handles.

    :param db: The Gramps database object.
    :param anchor_type: One of the ``_ANCHOR_KEYS`` values.
    :param anchor_val: The Gramps ID or filter name entered by the user.
    :param rule_name: The calling rule's name (for log messages).
    :returns: List of resolved Person handles; empty on failure.
    """
    if anchor_type == "person_id":
        person = db.get_person_from_gramps_id(anchor_val)
        if person is None:
            LOG.warning(_("%s: Person ID '%s' not found"), rule_name, anchor_val)
            return []
        return [person.get_handle()]

    if anchor_type == "person_filter":
        return _load_and_run_person_filter(db, anchor_val, rule_name)

    if anchor_type == "family_id":
        family = db.get_family_from_gramps_id(anchor_val)
        if family is None:
            LOG.warning(_("%s: Family ID '%s' not found"), rule_name, anchor_val)
            return []
        # Return handles of both partners as the "person anchor" set
        handles = []
        for h in (family.get_father_handle(), family.get_mother_handle()):
            if h:
                handles.append(h)
        return handles

    if anchor_type == "family_filter":
        fam_handles = _load_and_run_family_filter(db, anchor_val, rule_name)
        handles = []
        for fh in fam_handles:
            fam = db.get_family_from_handle(fh)
            if fam is None:
                continue
            for h in (fam.get_father_handle(), fam.get_mother_handle()):
                if h:
                    handles.append(h)
        return handles

    LOG.warning(_("%s: unknown anchor type '%s'"), rule_name, anchor_type)
    return []


def _resolve_family_anchors(
    db: object,
    anchor_type: str,
    anchor_val: str,
    rule_name: str,
) -> list[Family]:
    """
    Resolve the anchor selector to a list of Family objects.

    :param db: The Gramps database object.
    :param anchor_type: One of the ``_ANCHOR_KEYS`` values.
    :param anchor_val: The Gramps ID or filter name entered by the user.
    :param rule_name: The calling rule's name (for log messages).
    :returns: List of resolved Family objects; empty on failure.
    """
    if anchor_type == "family_id":
        family = db.get_family_from_gramps_id(anchor_val)
        if family is None:
            LOG.warning(_("%s: Family ID '%s' not found"), rule_name, anchor_val)
            return []
        return [family]

    if anchor_type == "family_filter":
        fam_handles = _load_and_run_family_filter(db, anchor_val, rule_name)
        return [
            db.get_family_from_handle(h)
            for h in fam_handles
            if db.get_family_from_handle(h) is not None
        ]

    if anchor_type == "person_id":
        person = db.get_person_from_gramps_id(anchor_val)
        if person is None:
            LOG.warning(_("%s: Person ID '%s' not found"), rule_name, anchor_val)
            return []
        return _families_of_person(db, person)

    if anchor_type == "person_filter":
        handles = _load_and_run_person_filter(db, anchor_val, rule_name)
        families = []
        for h in handles:
            person = db.get_person_from_handle(h)
            if person:
                families.extend(_families_of_person(db, person))
        return families

    LOG.warning(_("%s: unknown anchor type '%s'"), rule_name, anchor_type)
    return []


def _families_of_person(db: object, person: Person) -> list[Family]:
    """Return all Family objects where ``person`` is a member."""
    families = []
    for fh in (
        person.get_parent_family_handle_list()
        + person.get_family_handle_list()
    ):
        fam = db.get_family_from_handle(fh)
        if fam is not None:
            families.append(fam)
    return families


def _load_and_run_person_filter(
    db: object, filter_name: str, rule_name: str
) -> list[PersonHandle]:
    """Load and apply a named Person filter; return matching handles."""
    from gramps.gen.const import USER_FILTERS
    from gramps.gen.filters import FilterList

    fdb = FilterList(USER_FILTERS)
    fdb.load()
    named = next(
        (f for f in fdb.get_filters("Person") if f.get_name() == filter_name),
        None,
    )
    if named is None:
        LOG.warning(
            _("%s: Person filter '%s' not found"), rule_name, filter_name
        )
        return []
    return list(named.apply(db, db.iter_person_handles()))


def _load_and_run_family_filter(
    db: object, filter_name: str, rule_name: str
) -> list[FamilyHandle]:
    """Load and apply a named Family filter; return matching handles."""
    from gramps.gen.const import USER_FILTERS
    from gramps.gen.filters import FilterList

    fdb = FilterList(USER_FILTERS)
    fdb.load()
    named = next(
        (f for f in fdb.get_filters("Family") if f.get_name() == filter_name),
        None,
    )
    if named is None:
        LOG.warning(
            _("%s: Family filter '%s' not found"), rule_name, filter_name
        )
        return []
    return list(named.apply(db, db.iter_family_handles()))


# ============================================================
#
# ImmediateFamilyPeople  —  Person-output rule
#
# ============================================================


# ------------------------------------------------------------
#
# ImmediateFamilyPeople
#
# ------------------------------------------------------------
class ImmediateFamilyPeople(Rule):
    """
    Match people in the immediate families of a given anchor.

    The anchor can be any of: a Person ID, a Person filter name, a Family
    ID, or a Family filter name — selected via the combo box.  The rule
    then finds all Family records where any anchor person is a member
    (as partner or child) and returns the People in those families,
    filtered by the include checkboxes.

    :param list[str] list:
        ``[anchor_type, anchor_val, self, parents, siblings, spouses,
        children, in-laws, associations]``
    """

    labels = list(_RULE_LABELS)
    name = _("People in the immediate families of <anchor>")
    description = _(
        "Matches family members of a person or family anchor: "
        "parents, siblings, spouses, children, in-laws, and associations"
    )
    category = _("Family filters")
    allow_regex = False

    def prepare(self, db: object, user: object) -> None:
        """
        Pre-compute the set of matching Person handles once per filter run.

        :param db: The Gramps database object.
        :param user: The user object (used for progress reporting).
        """
        self.match_handles: set[PersonHandle] = set()
        anchor_type = self.list[_P_ANCHOR_TYPE]
        anchor_val = self.list[_P_ANCHOR_VAL]
        flags = _IncludeFlags(self.list[_P_SELF:])

        person_handles = _resolve_person_anchors(
            db, anchor_type, anchor_val, self.name
        )
        for handle in person_handles:
            person = db.get_person_from_handle(handle)
            if person:
                _collect_from_person(db, person, self.match_handles, flags)

    def apply(self, db: object, person: Person) -> bool:
        """
        Return True if ``person`` is in the pre-computed match set.

        :param db: The Gramps database object.
        :param person: The Person object being tested.
        :returns: True if the person matches.
        """
        return person.get_handle() in self.match_handles


# ============================================================
#
# ImmediateFamilyFamilies  —  Family-output rule
#
# ============================================================


# ------------------------------------------------------------
#
# ImmediateFamilyFamilies
#
# ------------------------------------------------------------
class ImmediateFamilyFamilies(Rule):
    """
    Match Family records in the immediate families of a given anchor.

    Returns the Family objects themselves rather than the People within
    them.  The anchor combo box and include checkboxes work identically
    to :class:`ImmediateFamilyPeople`.

    :param list[str] list:
        ``[anchor_type, anchor_val, self, parents, siblings, spouses,
        children, in-laws, associations]``
    """

    labels = list(_RULE_LABELS)
    name = _("Families in the immediate families of <anchor>")
    description = _(
        "Matches Family records linked to the immediate families of a "
        "person or family anchor"
    )
    category = _("Family filters")
    allow_regex = False

    def prepare(self, db: object, user: object) -> None:
        """
        Pre-compute the set of matching Family handles once per filter run.

        :param db: The Gramps database object.
        :param user: The user object (used for progress reporting).
        """
        self.match_handles: set[FamilyHandle] = set()
        anchor_type = self.list[_P_ANCHOR_TYPE]
        anchor_val = self.list[_P_ANCHOR_VAL]
        flags = _IncludeFlags(self.list[_P_SELF:])

        anchor_families = _resolve_family_anchors(
            db, anchor_type, anchor_val, self.name
        )
        for anchor_family in anchor_families:
            # Always include the anchor family itself
            self.match_handles.add(anchor_family.get_handle())
            _collect_family_handles(db, anchor_family, self.match_handles, flags)

    def apply(self, db: object, family: Family) -> bool:
        """
        Return True if ``family`` is in the pre-computed match set.

        :param db: The Gramps database object.
        :param family: The Family object being tested.
        :returns: True if the family matches.
        """
        return family.get_handle() in self.match_handles


# ---------------------------------------------------------------------------
#
# _collect_family_handles  — build Family handle set from one anchor Family
#
# ---------------------------------------------------------------------------
def _collect_family_handles(
    db: object,
    anchor_family: Family,
    match_fam_handles: set[FamilyHandle],
    flags: _IncludeFlags,
) -> None:
    """
    Add Family handles reachable from ``anchor_family`` to ``match_fam_handles``.

    - parents/siblings flags → child-of families of each partner.
    - spouses/children flags → other spouse-of families of each partner.
    - in-laws flag → child-of families of each partner's spouses.

    :param db: The Gramps database object.
    :param anchor_family: The anchor Family.
    :param match_fam_handles: Mutable set receiving matching Family handles.
    :param flags: Which relationship categories to include.
    """
    for partner_handle in (
        anchor_family.get_father_handle(),
        anchor_family.get_mother_handle(),
    ):
        if not partner_handle:
            continue
        partner = db.get_person_from_handle(partner_handle)
        if partner is None:
            continue

        if flags.include_parents or flags.include_siblings:
            for fh in partner.get_parent_family_handle_list():
                match_fam_handles.add(fh)

        spouse_handles: list[PersonHandle] = []
        if flags.include_spouses or flags.include_children or flags.include_inlaws:
            for fh in partner.get_family_handle_list():
                fam = db.get_family_from_handle(fh)
                if fam is None or fam.get_handle() == anchor_family.get_handle():
                    continue
                if flags.include_spouses or flags.include_children:
                    match_fam_handles.add(fh)
                if flags.include_inlaws:
                    for h in (fam.get_father_handle(), fam.get_mother_handle()):
                        if h and h != partner_handle:
                            spouse_handles.append(h)

        if flags.include_inlaws:
            for sh in spouse_handles:
                spouse = db.get_person_from_handle(sh)
                if spouse is None:
                    continue
                for fh in spouse.get_parent_family_handle_list():
                    match_fam_handles.add(fh)
