#!/usr/lib/python3/dist-packages/gramps/plugins/textreport/notelinkreport.py
"""
This report generator creates a text report listing the Gramps_Notes in the
Note_filter giving the Gramps_ID, Note_Type, Note_Text, and if applicable
The Link_Type (Gramps/Internet), if Gramps then whether the Link was valid,
and the Link itself. The listing can be sorted by ID or Note_Text.
"""
#
#
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015       Doug Blank <doug.blank@gmail.com>
#               2023       George Baynes <baynes@ntlworld.com>
#
# Forked to this NotReport.py
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
# version 2.0 Rewritten to allow use of Note-Filters and to output All Notes
#             also allows output to be sorted by Gramps_ID or Note_text

#
# standard python modules
#

import time

# -----------------------------------------------------------------------------------
# Gramps modules
# -----------------------------------------------------------------------------------
from gramps.gen.plug.docgen import (
    IndexMark,
    FontStyle,
    ParagraphStyle,
    FONT_SANS_SERIF,
    PARA_ALIGN_CENTER,
    FONT_SERIF,
    INDEX_TYPE_TOC,
)
from gramps.gen.plug.report import Report
from gramps.gen.plug.menu import StringOption, FilterOption, EnumeratedListOption
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.simple import SimpleAccess
from gramps.gen.lib import NoteType
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


##################
# NoteReport Class
##################
class NoteReport(Report):
    """
    This report produces a report of the Notes including any Links
    """

    def __init__(self, database, options, user):
        """
        Create the NoteLinkReport object that produces the report.

        The arguments are:

        database        - the GRAMPS database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.

        subtitle         - Subtitle of document
        filter           - Note Filter to define Notes to be included
        showsort         - 0 = None
                         - 1 = Sort by Note ID
                         - 2 = Source Note Text
        """

        # Set up the database
        Report.__init__(self, database, options, user)
        self.database = database
        # Set up the language to use from the Options menu
        self.menu = options.menu
        new_lang = self.menu.get_option_by_name("trans").get_value()
        self.locale = self.set_locale(new_lang)
        self._ = self.locale.translation.sgettext

    # end of __init__

    #####################
    # write_report method
    #####################
    def write_report(self):
        """
        The routine that actually creates the report.
        At this point, the document is opened and ready for writing.
        """
        note_handles = self.sort_data()
        if note_handles:
            self.print_title()
            # Print the body of the report
            self.write_note(note_handles)

    # end of Write_report method

    ####################
    # print_title method
    ####################
    def print_title(self):
        """
        Print title and Sub-title and Copyright Notice
        """
        # Print Report Title
        self.doc.start_paragraph("NLR-Title")
        title = self._("Note Report")
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        subtitle = self.menu.get_option_by_name("subtitle").get_value()
        if subtitle:
            # Print Report SubTitle
            self.doc.start_paragraph("NLR-Title")
            self.doc.write_text(f"{subtitle}")
            self.doc.end_paragraph()
        dateinfo = time.localtime(time.time())
        rname = self.database.get_researcher().get_name()
        copyrt = self._("Copyright") + " Ⓒ {} " + rname
        self.doc.start_paragraph("NLR-Copy")
        self.doc.write_text(f"{copyrt.format(dateinfo[0])}")
        self.doc.end_paragraph()

    ##################
    # sort_data method
    ##################
    def sort_data(
        self,
    ):
        """
        select notes to print and sort
        """
        # Get the sort method from the Options menu
        showsort = self.menu.get_option_by_name("showsort").get_value()
        # get the filter to use from the Options menu
        filter_option = self.menu.get_option_by_name("filter")
        if filter_option.get_filter().get_name() != "":
            # Use the selected filter to provide a list of filtered note handles
            notefilterlist = self.database.iter_note_handles()
            note_handles = filter_option.get_filter().apply(
                self.database, notefilterlist
            )
        else:
            # Or if no filter selected make a list of all the note handles
            note_handles = self.database.get_note_handles()
        # sort the note_handles file in order of Note ID order
        if showsort == "1":
            note_handles.sort(
                key=lambda x: self.database.get_note_from_handle(x).get_gramps_id()
            )
        # sort in order of Note Text
        if showsort == "2":
            note_handles.sort(key=lambda x: self.database.get_note_from_handle(x).get())
        return note_handles

    # end of sort_data method

    ###################
    # write_note method
    ###################
    def write_note(self, note_handles):
        """
        print note details
        """
        for noteh in note_handles:
            handle = self.database.get_note_from_handle(noteh).serialize()
            # (handle, gramps_id, text, format, type, change, tag_list, private)
            notestub = self.database.get_note_from_handle(noteh)
            # output the Gramps ID
            self.doc.start_paragraph("NLR-ID")
            self.doc.write_text(f"{notestub.get_gramps_id()}")
            self.doc.end_paragraph()
            # output the Note text with working links
            note_style = "NLR-Normal"
            links = False
            contains_html = notestub.get_type() == NoteType.HTML_CODE
            self.doc.write_styled_note(
                notestub.get_styledtext(),
                notestub.get_format(),
                note_style,
                contains_html=contains_html,
                links=links,
            )
            # output the Note Type
            self.doc.start_paragraph("NLR-Normal", f"{self._('Type')}")
            self.doc.write_text(f": {self._get_type(notestub.get_type())}")
            self.doc.end_paragraph()
            # output Tags
            self.doc.start_paragraph("NLR-Normal", f"{self._('Tags')}")
            if handle[6]:
                for tagh in handle[6]:
                    tag = self.database.get_tag_from_handle(tagh)
                    self.doc.write_text(f": {tag.get_name()}")
            else:
                self.doc.write_text(f": {self._('None')}")
            self.doc.end_paragraph()
            # output Privacy
            self.doc.start_paragraph("NLR-Normal", f"{self._('Privacy')}")
            if handle[7] is False:
                self.doc.write_text(f": {self._('Public')}")
            else:
                self.doc.write_text(f": {self._('Private')}")
            self.doc.end_paragraph()

    # end of write_note

    ####################
    # write_links method
    ####################
    def write_links(self, note):
        """
        prints all links to the report.
        """
        tagtype = ""
        tagcheck = ""
        tagvalue = ""
        sdb = SimpleAccess(self.database)
        for ldomain, ltype, lprop, lvalue in self.database.get_note_from_handle(
            note
        ).get_links():
            if ldomain == "gramps":
                tagtype = _(ltype)
                ref_obj = sdb.get_link(ltype, lprop, lvalue)
                if ref_obj:
                    tagvalue = sdb.describe(ref_obj)
                    tagcheck = "Ok"
                else:
                    tagvalue = f"{ldomain} : {ltype}/{lprop}/{lvalue}"
                    tagcheck = "Failed"
                self.doc.start_paragraph("NLR-Link", self._("Destination"))
                self.doc.write_text(": {self._(ldomain)}")
                self.doc.end_paragraph()
                self.doc.start_paragraph("NLR-Link", self._("Object"))
                self.doc.write_text(f": {self._(tagtype)}")
                self.doc.end_paragraph()
                self.doc.start_paragraph("NLR-Link", self._("Address"))
                self.doc.write_text(f": {tagvalue}")
                self.doc.write_text(f" {self._('Check')} = {tagcheck}")
                self.doc.end_paragraph()
            else:
                tagvalue = lvalue
                self.doc.start_paragraph("NLR-Link", self._("Destination"))
                self.doc.write_text(f": {self._(ldomain)}")
                self.doc.end_paragraph()
                self.doc.start_paragraph("NLR-Link", self._("Address"))
                self.doc.write_text(f": {lvalue}")
                self.doc.end_paragraph()


# end of write_links method


###################
# NoteOptions Class
###################
class NoteOptions(MenuReportOptions):
    """
    Class to setup Options for the report
    """

    def __init__(self, name, dbase):
        """
        Initiallise the options for this report
        """
        self.__filter = None
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        # Return a string that describes the subject of the report.
        return self.__filter.get_filter().get_name()

    # Set up options
    def add_menu_options(self, menu):
        """
        Add the options for this report
        """
        category_name = "Report Options"
        # Title of the Report is fixed at ""Note Report""

        # Subtitle of the Report
        subtitle = StringOption(_("Subtitle"), _("Subtitle of the Report"))
        subtitle.set_help(_("Subtitle string for the report."))
        menu.add_option("Report Options", "subtitle", subtitle)

        # Reload filters to pick any new ones created since Gramps was loaded
        from gramps.gen.filters import CustomFilters, GenericFilter

        self.__filter = FilterOption(_("Select using filter"), 0)
        self.__filter.set_help(_("Select Notes using a Note filter"))
        filter_list = []
        filter_list.append(GenericFilter())
        filter_list.extend(CustomFilters.get_filters("Note"))
        self.__filter.set_filters(filter_list)
        menu.add_option(category_name, "filter", self.__filter)
        # Sort Order?
        showsort = EnumeratedListOption("Sort Order", "1")
        showsort.set_items(
            [
                ("0", _("No Sort")),
                ("1", _("Sort by Note ID")),
                ("2", _("Sort by Note Text")),
            ]
        )
        showsort.set_help(_("Select Sort Option from list"))
        menu.add_option(category_name, "showsort", showsort)
        # Location for Language
        stdoptions.add_localization_option(menu, "Report Options")

    # dates are not output by this report
    #        stdoptions.add_date_format_option(menu, category_name, locale_opt)

    # Paragraph Styles
    def make_default_style(self, default_style):
        """
        Make the default output style for the Note Report.
        """
        #       Define the style used for the report title
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=16, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the title/subtitle of the report."))
        default_style.add_paragraph_style("NLR-Title", para)
        #       Define the style used for the copyright
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=12, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the copyright of the report."))
        default_style.add_paragraph_style("NLR-Copy", para)
        #       Define the style used for the Note ID
        font = FontStyle()
        font.set(face=FONT_SERIF, size=12, italic=0, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_first_indent(0.0)
        para.set_left_margin(0.0)
        para.set_top_margin(0.1)
        para.set_bottom_margin(0.1)
        ParagraphStyle().set_description(
            _("The basic style used for the Note ID display.")
        )
        default_style.add_paragraph_style("NLR-ID", para)
        #       Define the style used for the Notes
        font = FontStyle()
        font.set(face=FONT_SERIF, size=12, italic=0, bold=0)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_first_indent(0.0)
        para.set_left_margin(1.0)
        para.set_top_margin(0.1)
        para.set_bottom_margin(0.1)
        ParagraphStyle().set_description(_("The basic style used for the Notes."))
        default_style.add_paragraph_style("NLR-Normal", para)
        #       Define the style used for the Links
        font = FontStyle()
        font.set(face=FONT_SERIF, size=11, italic=1, bold=0)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(0.1)
        para.set_bottom_margin(0.1)
        para.set_first_indent(-2.1)
        para.set_left_margin(4.0)
        para.set_description(_("The style used for the Link display."))
        default_style.add_paragraph_style("NLR-Link", para)
