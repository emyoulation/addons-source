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
#   a single rule covers all variants; two rules total — Person-output and
#   Family-output."

_URL = "https://gramps.discourse.group/t/addon-filter-rule-requests/4148"
_AUTHORS = ["Claude Sonnet 4.5, Anthropic"]
_EMAIL = ["https://www.anthropic.com"]
_FNAME = "FamilyNetworkRules.py"
_VERSION = "0.1.0"
_TARGET = "6.0"

register(
    RULE,
    id="FamilyNetworkRules_ImmediateFamilyPeople",
    name=_("People in the immediate families of <anchor>"),
    description=_(
        "Matches family members of a person or family anchor: "
        "parents, siblings, spouses, children, in-laws, and associations"
    ),
    version=_VERSION,
    gramps_target_version=_TARGET,
    status=UNSTABLE,
    fname=_FNAME,
    ruleclass="ImmediateFamilyPeople",
    namespace="Person",
    authors=_AUTHORS,
    authors_email=_EMAIL,
    help_url=_URL,
)

register(
    RULE,
    id="FamilyNetworkRules_ImmediateFamilyFamilies",
    name=_("Families in the immediate families of <anchor>"),
    description=_(
        "Matches Family records linked to the immediate families of a "
        "person or family anchor"
    ),
    version=_VERSION,
    gramps_target_version=_TARGET,
    status=UNSTABLE,
    fname=_FNAME,
    ruleclass="ImmediateFamilyFamilies",
    namespace="Family",
    authors=_AUTHORS,
    authors_email=_EMAIL,
    help_url=_URL,
)
