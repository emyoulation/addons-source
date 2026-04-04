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
# Prompts: "Rename FamilyNetworkRules to use 'immediate families' vocabulary;
#   add MyBoolean checkbox parameters for self/parents/siblings/spouses/
#   children/in-laws/associations; implement in-law traversal (parents and
#   siblings of each spouse) and association traversal (PersonRef list);
#   extract shared _collect_immediate_families() helper and _IncludeFlags
#   parser; keep prepare()/apply() pattern; update .gpr.py, README,
#   ADVANCED, tests, and commit template."

# ------------------------
# Python modules
# ------------------------
import unittest
from unittest.mock import MagicMock, patch

# ------------------------
# Gramps modules
# ------------------------
try:
    from gramps.gen.lib import Person, Family, ChildRef

    GRAMPS_AVAILABLE = True
except ImportError:
    GRAMPS_AVAILABLE = False

# ------------------------
# Gramps specific
# ------------------------
if GRAMPS_AVAILABLE:
    from FamilyNetworkRules import (
        ImmediateFamilyPeople,
        ImmediateFamilyPeopleFromFilter,
        _IncludeFlags,
        _collect_immediate_families,
    )

# ---------------------------------------------------------------------------
# Shared mock-builder helpers
# ---------------------------------------------------------------------------

ALL_ON = ["1", "1", "1", "1", "1", "1", "1"]
ALL_OFF = ["0", "0", "0", "0", "0", "0", "0"]


def _flags(self=1, parents=1, siblings=1, spouses=1, children=1, inlaws=1, assoc=1):
    """Return an _IncludeFlags with the given boolean values."""
    return _IncludeFlags(
        [str(self), str(parents), str(siblings),
         str(spouses), str(children), str(inlaws), str(assoc)]
    )


def _make_person(handle, parent_fams=None, spouse_fams=None, assoc_refs=None):
    """Build a minimal mock Person."""
    p = MagicMock(spec=Person)
    p.get_handle.return_value = handle
    p.get_parent_family_handle_list.return_value = parent_fams or []
    p.get_family_handle_list.return_value = spouse_fams or []
    refs = []
    for ref_handle in (assoc_refs or []):
        r = MagicMock()
        r.ref = ref_handle
        refs.append(r)
    p.get_person_ref_list.return_value = refs
    return p


def _make_child_ref(handle):
    ref = MagicMock(spec=ChildRef)
    ref.ref = handle
    return ref


def _make_family(fam_handle, father=None, mother=None, children=None):
    """Build a minimal mock Family."""
    fam = MagicMock(spec=Family)
    fam.get_handle.return_value = fam_handle
    fam.get_father_handle.return_value = father
    fam.get_mother_handle.return_value = mother
    fam.get_child_ref_list.return_value = [
        _make_child_ref(h) for h in (children or [])
    ]
    return fam


def _make_db(persons_by_handle, families_by_handle, persons_by_gid=None):
    """Build a mock db from dicts keyed by handle."""
    db = MagicMock()
    db.get_person_from_handle.side_effect = lambda h: persons_by_handle.get(h)
    db.get_family_from_handle.side_effect = lambda h: families_by_handle.get(h)
    if persons_by_gid:
        db.get_person_from_gramps_id.side_effect = lambda gid: persons_by_gid.get(gid)
    return db


# ---------------------------------------------------------------------------
# _IncludeFlags tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(GRAMPS_AVAILABLE, "Gramps not installed")
class TestIncludeFlags(unittest.TestCase):
    """Unit tests for the _IncludeFlags parameter parser."""

    def test_all_on(self):
        f = _IncludeFlags(["1", "1", "1", "1", "1", "1", "1"])
        self.assertTrue(all([
            f.include_self, f.include_parents, f.include_siblings,
            f.include_spouses, f.include_children,
            f.include_inlaws, f.include_assoc,
        ]))

    def test_all_off(self):
        f = _IncludeFlags(["0", "0", "0", "0", "0", "0", "0"])
        self.assertFalse(any([
            f.include_self, f.include_parents, f.include_siblings,
            f.include_spouses, f.include_children,
            f.include_inlaws, f.include_assoc,
        ]))

    def test_missing_index_defaults_true(self):
        """A truncated list should default missing flags to True."""
        f = _IncludeFlags([])
        self.assertTrue(f.include_self)
        self.assertTrue(f.include_assoc)

    def test_selective(self):
        f = _IncludeFlags(["1", "0", "1", "0", "1", "0", "1"])
        self.assertTrue(f.include_self)
        self.assertFalse(f.include_parents)
        self.assertTrue(f.include_siblings)
        self.assertFalse(f.include_spouses)
        self.assertTrue(f.include_children)
        self.assertFalse(f.include_inlaws)
        self.assertTrue(f.include_assoc)


# ---------------------------------------------------------------------------
# _collect_immediate_families tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(GRAMPS_AVAILABLE, "Gramps not installed")
class TestCollectImmediateFamilies(unittest.TestCase):
    """Direct tests of the shared traversal helper."""

    def _run(self, anchor, persons_by_handle, families_by_handle, flags):
        db = _make_db(persons_by_handle, families_by_handle)
        result: set = set()
        _collect_immediate_families(db, anchor, result, flags)
        return result

    def test_self_included_when_flag_on(self):
        anchor = _make_person("A")
        result = self._run(anchor, {"A": anchor}, {}, _flags())
        self.assertIn("A", result)

    def test_self_excluded_when_flag_off(self):
        anchor = _make_person("A")
        result = self._run(anchor, {"A": anchor}, {}, _flags(self=0))
        self.assertNotIn("A", result)

    def test_parents_included(self):
        anchor = _make_person("C", parent_fams=["F1"])
        fam = _make_family("F1", father="DAD", mother="MOM", children=["C"])
        result = self._run(anchor, {}, {"F1": fam}, _flags())
        self.assertIn("DAD", result)
        self.assertIn("MOM", result)

    def test_parents_excluded_when_flag_off(self):
        anchor = _make_person("C", parent_fams=["F1"])
        fam = _make_family("F1", father="DAD", children=["C"])
        result = self._run(anchor, {}, {"F1": fam}, _flags(parents=0))
        self.assertNotIn("DAD", result)

    def test_siblings_included(self):
        anchor = _make_person("C", parent_fams=["F1"])
        fam = _make_family("F1", children=["C", "SIB"])
        result = self._run(anchor, {}, {"F1": fam}, _flags())
        self.assertIn("SIB", result)
        self.assertNotIn("C", result)  # anchor not double-added via sibling list

    def test_siblings_excluded_when_flag_off(self):
        anchor = _make_person("C", parent_fams=["F1"])
        fam = _make_family("F1", children=["C", "SIB"])
        result = self._run(anchor, {}, {"F1": fam}, _flags(siblings=0))
        self.assertNotIn("SIB", result)

    def test_spouse_included(self):
        anchor = _make_person("A", spouse_fams=["F2"])
        fam = _make_family("F2", father="A", mother="SP")
        result = self._run(anchor, {}, {"F2": fam}, _flags())
        self.assertIn("SP", result)

    def test_spouse_excluded_when_flag_off(self):
        anchor = _make_person("A", spouse_fams=["F2"])
        fam = _make_family("F2", father="A", mother="SP")
        result = self._run(anchor, {}, {"F2": fam}, _flags(spouses=0, inlaws=0))
        self.assertNotIn("SP", result)

    def test_children_included(self):
        anchor = _make_person("A", spouse_fams=["F2"])
        fam = _make_family("F2", father="A", children=["KID"])
        result = self._run(anchor, {}, {"F2": fam}, _flags())
        self.assertIn("KID", result)

    def test_children_excluded_when_flag_off(self):
        anchor = _make_person("A", spouse_fams=["F2"])
        fam = _make_family("F2", father="A", children=["KID"])
        result = self._run(anchor, {}, {"F2": fam}, _flags(children=0))
        self.assertNotIn("KID", result)

    def test_inlaws_included(self):
        """In-laws: parents and siblings of the spouse."""
        spouse = _make_person("SP", parent_fams=["SPFAM"])
        anchor = _make_person("A", spouse_fams=["F2"])
        spouse_fam = _make_family("F2", father="A", mother="SP")
        inlaw_fam = _make_family("SPFAM", father="FIL", mother="MIL",
                                 children=["SP", "SIL"])
        result = self._run(
            anchor,
            {"SP": spouse},
            {"F2": spouse_fam, "SPFAM": inlaw_fam},
            _flags(),
        )
        self.assertIn("FIL", result)   # father-in-law
        self.assertIn("MIL", result)   # mother-in-law
        self.assertIn("SIL", result)   # sibling-in-law

    def test_inlaws_excluded_when_flag_off(self):
        spouse = _make_person("SP", parent_fams=["SPFAM"])
        anchor = _make_person("A", spouse_fams=["F2"])
        spouse_fam = _make_family("F2", father="A", mother="SP")
        inlaw_fam = _make_family("SPFAM", father="FIL", children=["SP"])
        result = self._run(
            anchor,
            {"SP": spouse},
            {"F2": spouse_fam, "SPFAM": inlaw_fam},
            _flags(inlaws=0),
        )
        self.assertNotIn("FIL", result)

    def test_associations_included(self):
        anchor = _make_person("A", assoc_refs=["FRIEND"])
        result = self._run(anchor, {}, {}, _flags())
        self.assertIn("FRIEND", result)

    def test_associations_excluded_when_flag_off(self):
        anchor = _make_person("A", assoc_refs=["FRIEND"])
        result = self._run(anchor, {}, {}, _flags(assoc=0))
        self.assertNotIn("FRIEND", result)

    def test_none_family_handle_skipped(self):
        """A None return from get_family_from_handle must not crash."""
        anchor = _make_person("A", parent_fams=["MISSING"])
        db = _make_db({}, {"MISSING": None})
        result: set = set()
        _collect_immediate_families(db, anchor, result, _flags())
        # Only self should be in the result
        self.assertEqual(result, {"A"})

    def test_anchor_not_added_as_own_sibling(self):
        """The anchor should not appear in the sibling list of its own family."""
        anchor = _make_person("A", parent_fams=["F1"])
        fam = _make_family("F1", children=["A", "B"])
        result = self._run(anchor, {}, {"F1": fam}, _flags(self=0))
        self.assertNotIn("A", result)
        self.assertIn("B", result)


# ---------------------------------------------------------------------------
# ImmediateFamilyPeople rule tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(GRAMPS_AVAILABLE, "Gramps not installed")
class TestImmediateFamilyPeople(unittest.TestCase):
    """Integration tests for the ImmediateFamilyPeople rule."""

    def _make_rule(self, gramps_id, flags_list=None):
        params = [gramps_id] + (flags_list if flags_list is not None else ALL_ON)
        return ImmediateFamilyPeople(params)

    def test_unknown_id_warns_and_matches_nothing(self):
        rule = self._make_rule("X9999")
        db = MagicMock()
        db.get_person_from_gramps_id.return_value = None
        with self.assertLogs("FamilyNetworkRules", level="WARNING"):
            rule.prepare(db, None)
        stranger = _make_person("H_stranger")
        self.assertFalse(rule.apply(db, stranger))

    def test_all_flags_on_includes_expected_members(self):
        anchor = _make_person("A", parent_fams=["PF"], spouse_fams=["SF"])
        parent_fam = _make_family("PF", father="DAD", children=["A", "SIB"])
        spouse_fam = _make_family("SF", father="A", mother="SP", children=["KID"])
        db = _make_db(
            {"A": anchor},
            {"PF": parent_fam, "SF": spouse_fam},
            {"I0001": anchor},
        )
        rule = self._make_rule("I0001")
        rule.prepare(db, None)

        for expected in ["A", "DAD", "SIB", "SP", "KID"]:
            person = _make_person(expected)
            self.assertTrue(rule.apply(db, person), f"{expected} should match")

    def test_children_only_flag(self):
        anchor = _make_person("A", parent_fams=["PF"], spouse_fams=["SF"])
        parent_fam = _make_family("PF", father="DAD", children=["A", "SIB"])
        spouse_fam = _make_family("SF", father="A", mother="SP", children=["KID"])
        db = _make_db(
            {"A": anchor},
            {"PF": parent_fam, "SF": spouse_fam},
            {"I0001": anchor},
        )
        children_only = ["0", "0", "0", "0", "1", "0", "0"]
        rule = self._make_rule("I0001", children_only)
        rule.prepare(db, None)

        self.assertTrue(rule.apply(db, _make_person("KID")))
        self.assertFalse(rule.apply(db, _make_person("DAD")))
        self.assertFalse(rule.apply(db, _make_person("SP")))
        self.assertFalse(rule.apply(db, _make_person("SIB")))
        self.assertFalse(rule.apply(db, _make_person("A")))

    def test_prepare_twice_resets_state(self):
        """A second prepare() call must not retain handles from the first."""
        anchor1 = _make_person("A1")
        anchor2 = _make_person("A2")
        db = MagicMock()
        rule = self._make_rule("I0001")

        db.get_person_from_gramps_id.return_value = anchor1
        rule.prepare(db, None)
        self.assertTrue(rule.apply(db, anchor1))

        db.get_person_from_gramps_id.return_value = anchor2
        rule.prepare(db, None)
        self.assertFalse(rule.apply(db, anchor1))
        self.assertTrue(rule.apply(db, anchor2))


if __name__ == "__main__":
    unittest.main()
