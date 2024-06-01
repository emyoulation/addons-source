#
# Gramps - a GTK+/GNOME based genealogy program
#
# Forked from NoteLinkReport
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# ------------------------------------------------------------------------
#
# Note Report
#
# ------------------------------------------------------------------------
from gramps.version import major_version, VERSION_TUPLE

help_url = "https://gramps-project.org/wiki/index.php/Addon:Note_Report"

if VERSION_TUPLE < (5, 2, 0):
    additional_args = {}
else:
    additional_args = {
        "audience": EVERYONE,
        "help_url": help_url,
    }

register(
    REPORT,
    id="note_report",
    name=_("Note Report"),
    description=_("Provides a list of Notes limited by Note Filter"),
    version="1.0.1",
    gramps_target_version=major_version,
    status=STABLE,
    fname="note_report.py",
    authors=["George Baynes"],
    authors_email=["baynes@ntlworld.com"],
    category=CATEGORY_TEXT,
    reportclass="NoteReport",
    optionclass="NoteOptions",
    report_modes=[REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI],
    require_active=False,
    **additional_args,
)
