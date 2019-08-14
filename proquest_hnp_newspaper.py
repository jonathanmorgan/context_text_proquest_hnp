from __future__ import unicode_literals

'''
Copyright 2019 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text_proquest_hnp.

context_text_proquest_hnp is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text_proquest_hnp is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text_proquest_hnp. If not, see http://www.gnu.org/licenses/.
'''

#===============================================================================
# imports (in alphabetical order by package, then by name)
#===============================================================================


# python base imports
import calendar
#from datetime import date
import datetime

# django classes
from django.contrib.auth.models import User
from django.db.models import Q

# python_utilities
from python_utilities.parameters.param_container import ParamContainer
from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited

# context
from context_text.shared.context_text_base import ContextTextBase

#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class ProquestHNPNewspaper( ContextTextBase ):


    #---------------------------------------------------------------------------
    # ! ==> CONSTANTS-ish
    #---------------------------------------------------------------------------


    # Dictionary of parameters to their types, for use in debug method.
    PARAM_NAME_TO_TYPE_MAP = {}


    #-----------------------------------------------------------------------------
    # ! ==> class methods
    #-----------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    # ! ==> __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( ProquestHNPNewspaper, self ).__init__()

        # declare variables
        self.request = None
        self.parameters = ParamContainer()
        
        # rate limiting
        self.is_rate_limited = False
        
        # information on proquest data files
        self.paper_identifier = None
        self.archive_identifier = None
        self.source_all_papers_folder = None
        self.source_paper_path = None
        self.destination_all_papers_folder = None
        self.destination_paper_path = None

        # define parameters - should do this in "child.__init__()".
        self.define_parameters( self.PARAM_NAME_TO_TYPE_MAP )        
        
        # set logger name (for LoggingHelper parent class: (LoggingHelper --> BasicRateLimited --> ContextTextBase).
        self.set_logger_name( "context_text_proquest_hnp.proquest_hnp_newspaper" )
        
    #-- END method __init__() --#


    #---------------------------------------------------------------------------
    # ! ==> instance methods, in alphabetical order
    #---------------------------------------------------------------------------


#-- END class ProquestHNPNewspaper --#