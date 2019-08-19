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
import datetime
import glob
import os
import six
import xmltodict
import zipfile

# django classes
from django.contrib.auth.models import User
from django.db.models import Q
from django.template.defaultfilters import slugify

# python_utilities
from python_utilities.exceptions.exception_helper import ExceptionHelper
from python_utilities.parameters.param_container import ParamContainer
from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited

# context_text
from context_text.shared.context_text_base import ContextTextBase

# context_text_proquest_hnp
from context_text_proquest_hnp.models import PHNP_Newspaper_Archive_Object_Type
from context_text_proquest_hnp.models import PHNP_Newspaper_Object_Type
from context_text_proquest_hnp.models import Proquest_HNP_Newspaper
from context_text_proquest_hnp.models import Proquest_HNP_Newspaper_Archive
from context_text_proquest_hnp.models import Proquest_HNP_Object_Type
from context_text_proquest_hnp.models import Proquest_HNP_Object_Type_Raw_Value

#===============================================================================
# classes (in alphabetical order by name)
#===============================================================================

class ProquestHNPNewspaperHelper( ContextTextBase ):


    #---------------------------------------------------------------------------
    # ! ==> CONSTANTS-ish
    #---------------------------------------------------------------------------


    # Dictionary of parameters to their types, for use in debug method.
    PARAM_NAME_TO_TYPE_MAP = {}


    # archive summary
    ARCHIVE_SUMMARY_TYPE_TO_COUNT_MAP = "type_to_count_map"
    ARCHIVE_SUMMARY_MIN_PUB_DATE = "min_pub_date"
    ARCHIVE_SUMMARY_MAX_PUB_DATE = "max_pub_date"
    ARCHIVE_SUMMARY_INSTANCE = "archive_instance"
    
    # datetime string formats
    DATETIME_FORMAT_NUMERAL_PUB_DATE = "%Y%m%d"

    # logger name
    MY_LOGGER_NAME = "context_text_proquest_hnp.proquest_hnp_newspaper_helper"


    #---------------------------------------------------------------------------
    # ! ==> class variables
    #---------------------------------------------------------------------------


    # object type instances, to minimize trips to database.
    raw_object_type_to_instance_map = {}

    
    #---------------------------------------------------------------------------
    # ! ==> class methods
    #---------------------------------------------------------------------------


    @classmethod
    def get_all_object_types( cls ):
        
        # return reference
        list_OUT = None
        
        # declare variables
        object_type_qs = None
        
        # get all in QS.
        object_type_qs = Proquest_HNP_Object_Type.objects.all()
        object_type_qs = object_type_qs.order_by( "raw_value" )
        
        # get list of raw values
        object_type_qs = object_type_qs.values_list( "raw_value", flat = True )
        list_OUT = list( object_type_qs )
        
        return list_OUT
        
    #-- END class method get_all_object_types() --#
    

    @classmethod
    def fetch_object_type_instance( cls, raw_value_IN ):
        
        # return reference
        instance_OUT = None

        # declare variables
        me = "fetch_object_type_instance"
        slug_value = None
        log_message = None
        type_instance = None
        db_raw_value = None
        raw_value_qs = None
        raw_value_count = None
        raw_value_instance = None
        
        # make sure value is passed in.
        if ( ( raw_value_IN is not None ) and ( raw_value_IN != "" ) ):
        
            # slugify the value
            slug_value = slugify( raw_value_IN )
        
            # is value already in our map?
            if ( raw_value_IN in cls.raw_object_type_to_instance_map ):
            
                # it is.  Return what we have.
                type_instance = cls.raw_object_type_to_instance_map.get( raw_value_IN, None )
                
            else:
            
                # not in cache.  In database?
                try:
                
                    # look to see if type with this slug exists.
                    type_instance = Proquest_HNP_Object_Type.objects.get( raw_value = raw_value_IN )
                    
                    # call method set_raw_value() with the value passed in to
                    #     set the current raw value - if matches main value in
                    #     the object type record, does nothing except to make
                    #     sure the value is also in the overflow area.  If the
                    #     value passed in is different from main record, adds it
                    #     to the overflow table.
                    type_instance.set_raw_value( raw_value_IN )
                    type_instance.save()
                    
                except Proquest_HNP_Object_Type.DoesNotExist as dnee:
                
                    # does not exist.  make one and return it.
                    type_instance = Proquest_HNP_Object_Type()
                    type_instance.set_raw_value( raw_value_IN )
                    type_instance.save()
                
                except Proquest_HNP_Object_Type.MultipleObjectsReturned as more:
                
                    # ERROR - more than one.  Should be impossible.  Check
                    #     case-sensitivity things.
                    log_message = "ERROR - multiple matches for raw value \"{}\" ( slug \"{}\" ).".format( slug_value, raw_value_IN )
                    cls.log_message( log_message,
                                     method_IN = me,
                                     logger_name_IN = cls.MY_LOGGER_NAME,
                                     do_print_IN = True )
                    type_instance = None
                
                except Exception as e:
                
                    # Unexpected ERROR.
                    log_message = "ERROR - Unexpected exception caught trying to retrieve object type instance for raw value \"{}\" ( slug \"\" ).".format( slug_value, raw_value_IN )
                    cls.log_exception( e,
                                       message_IN = log_message,
                                       method_IN = me,
                                       logger_name_IN = cls.MY_LOGGER_NAME,
                                       do_print_IN = True )
                    type_instance = None
                
                #-- END try-except --#
                
                # got anything?
                if ( type_instance is not None ):
                
                    # yes.  Add to map.
                    cls.raw_object_type_to_instance_map[ raw_value_IN ] = type_instance
                    type_instance = cls.fetch_object_type_instance( raw_value_IN )
                
                #-- END check to see if we have an instance --#
                 
            #-- END check to see if instance already loaded --#
            
        #-- END check to make sure value passed in. --#
        
        instance_OUT = type_instance
        return instance_OUT
        
    #-- END class method fetch_object_type_instance() --#
    

    @classmethod
    def fetch_archive_instance( cls,
                                proquest_hnp_newspaper_instance_IN,
                                archive_identifier_IN,
                                compressed_file_path_IN = None,
                                uncompressed_folder_path_IN = None,
                                start_date_IN = None,
                                end_date_IN = None,
                                notes_IN = None ):
        
        # return reference
        instance_OUT = None

        # declare variables
        me = "fetch_archive_instance"
        log_message = None
        archive_qs = None
        archive_instance = None
        
        # make sure newspaper passed in...
        if ( proquest_hnp_newspaper_instance_IN is not None ):
        
            # ...and identifier passed in.
            if ( ( archive_identifier_IN is not None ) and ( archive_identifier_IN != "" ) ):

                # build query set
                archive_qs = Proquest_HNP_Newspaper_Archive.objects.filter( proquest_hnp_newspaper = proquest_hnp_newspaper_instance_IN )
                archive_qs = archive_qs.filter( archive_identifier = archive_identifier_IN )

                # In database?
                try:
                
                    # look to see if type with this raw value exists.
                    archive_instance = archive_qs.get()
                    
                except Proquest_HNP_Newspaper_Archive.DoesNotExist as dnee:
                
                    # does not exist.  make one and return it.
                    archive_instance = Proquest_HNP_Newspaper_Archive()
                    archive_instance.proquest_hnp_newspaper = proquest_hnp_newspaper_instance_IN
                    archive_instance.archive_identifier = archive_identifier_IN
                    archive_instance.compressed_file_path = compressed_file_path_IN
                    archive_instance.uncompressed_folder_path = uncompressed_folder_path_IN
                    archive_instance.start_date = start_date_IN
                    archive_instance.end_date = end_date_IN
                    archive_instance.notes = notes_IN
                    archive_instance.save()
                
                except Proquest_HNP_Newspaper_Archive.MultipleObjectsReturned as more:
                
                    # ERROR - more than one.  Should be impossible.  Check
                    #     case-sensitivity things.
                    log_message = "ERROR - multiple matches for archive_identifier = \"{}\".  This should be impossible.  Check for case-insensitivity.".format( archive_identifier )
                    cls.log_message( log_message,
                                     method_IN = me,
                                     logger_name_IN = cls.MY_LOGGER_NAME,
                                     do_print_IN = True )
                    archive_instance = None
                
                except Exception as e:
                
                    # Unexpected ERROR.
                    log_message = "ERROR - Unexpected exception caught loading Proquest_HNP_Newspaper_Archive with archive_identifier = \"{}\"".format( archive_identifier )
                    cls.log_exception( e,
                                       message_IN = log_message,
                                       method_IN = me,
                                       logger_name_IN = cls.MY_LOGGER_NAME,
                                       do_print_IN = True )
                    archive_instance = None
                
                #-- END try-except --#
                
            #-- END check to make sure archive_identifier passed in. --#
            
        #-- END check to make sure newspaper instance passed in. --#
        
        instance_OUT = archive_instance
        return instance_OUT
        
    #-- END class method fetch_archive_instance() --#


    #---------------------------------------------------------------------------
    # ! ==> __init__() method
    #---------------------------------------------------------------------------


    def __init__( self ):

        # call parent's __init__()
        super( ProquestHNPNewspaperHelper, self ).__init__()

        # declare variables
        self.request = None
        self.parameters = ParamContainer()
        
        # rate limiting
        self.is_rate_limited = False
        
        # information on proquest data files
        self.paper_identifier = None
        self.paper_start_year = None
        self.paper_end_year = None
        self.archive_identifier = None
        self.source_all_papers_folder = None
        self.source_paper_path = None
        self.destination_all_papers_folder = None
        self.destination_paper_path = None
        self.did_destination_paper_path_exist = None
        
        # references to django model instances
        self.phnp_newspaper = None
        self.newspaper = None
        
        # metadata about article files
        self.object_type_to_count_map = None

        # define parameters - should do this in "child.__init__()".
        self.define_parameters( self.PARAM_NAME_TO_TYPE_MAP )        
        
        # set logger name (for LoggingHelper parent class: (LoggingHelper --> ExceptionHelper --> BasicRateLimited --> ContextBase --> ContextTextBase).
        self.set_logger_name( self.MY_LOGGER_NAME )
        
    #-- END method __init__() --#


    def __str__( self ):

        # return reference
        value_OUT = ""
        
        # declare variables
        separator = ""
        
        if ( self.paper_identifier is not None ):
        
            value_OUT = "{}{}{}".format( value_OUT, separator, self.paper_identifier )
            separator = " - "
            
        #-- END check if ID present --#
        
        if ( self.paper_start_year is not None ):
        
            value_OUT = "{} from {}".format( value_OUT, self.paper_start_year )
            separator = " - "
            
        #-- END check if start year present --#

        if ( self.paper_end_year is not None ):
        
            value_OUT = "{} to {}".format( value_OUT, self.paper_end_year )
            separator = " - "
            
        #-- END check if end year present --#
            
        if ( self.source_paper_path is not None ):
        
            value_OUT = "{}{}source path: {}".format( value_OUT, separator, self.source_paper_path )
            separator = " - "
            
        #-- END check if source path present --#
            
        if ( self.destination_paper_path is not None ):
        
            value_OUT = "{}{}dest path: {}".format( value_OUT, separator, self.destination_paper_path )
            separator = " - "
            
        #-- END check if dest path present --#
        
        return value_OUT
            
    #-- END method __str__() --#


    #---------------------------------------------------------------------------
    # ! ==> instance methods, in alphabetical order
    #---------------------------------------------------------------------------


    def create_PHNP_newspaper( self ):
        
        '''
        Instance must have paper_identifier set.  If set, start and end year and
            source and destination paths will also be stored.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "create_PHNP_newspaper"
        log_message = None
        paper_qs = None
        paper_count = -1
        phnp_newspaper_instance = None
        paper_identifier = None
        start_year = None
        end_year = None
        compressed_folder_path = None
        uncompressed_folder_path = None
        newspaper = None
        notes = None
        
        # get data from instance
        paper_identifier = self.paper_identifier
        start_year = self.paper_start_year
        end_year = self.paper_end_year
        compressed_folder_path = self.source_paper_path
        uncompressed_folder_path = self.destination_paper_path
        newspaper = self.newspaper
        
        # try to retrieve from database
        paper_qs = Proquest_HNP_Newspaper.objects.filter( paper_identifier = paper_identifier )
        paper_count = paper_qs.count()
        
        # anything returned?
        if ( paper_count == 0 ):
        
            # make a new instance
            phnp_newspaper_instance = Proquest_HNP_Newspaper()

            # store information
            phnp_newspaper_instance.paper_identifier = paper_identifier
            phnp_newspaper_instance.start_year = start_year
            phnp_newspaper_instance.end_year = end_year
            phnp_newspaper_instance.compressed_folder_path = compressed_folder_path
            phnp_newspaper_instance.uncompressed_folder_path = uncompressed_folder_path
            phnp_newspaper_instance.newspaper = newspaper
            
            # save
            phnp_newspaper_instance.save()
                    
        else:
            
            log_message = "In {}: Proquest_HNP_Newspaper already exists for paper_identifier \"{}\".  Returning existing instance.".format( me, paper_identifier )
            self.output_debug_message( log_message, do_print_IN = True )
            phnp_newspaper_instance = paper_qs.get()
            
        #-- END check if exists --#
            
        # store in instance
        self.phnp_newspaper = phnp_newspaper_instance
        
        # return
        instance_OUT = self.phnp_newspaper
        return instance_OUT
        
    #-- END method create_PHNP_newspaper() --#
    

    def get_archive_instance( self,
                              archive_identifier_IN,
                              compressed_file_path_IN = None,
                              uncompressed_folder_path_IN = None,
                              start_date_IN = None,
                              end_date_IN = None,
                              notes_IN = None ):
        
        # return reference
        instance_OUT = None

        # declare variables
        me = "get_archive_instance"
        newspaper_instance = None
        archive_instance = None

        # get nested newspaper instance
        newspaper_instance = self.phnp_newspaper
        
        # call static method
        archive_instance = self.fetch_archive_instance( newspaper_instance,
                                                        archive_identifier_IN,
                                                        compressed_file_path_IN,
                                                        uncompressed_folder_path_IN,
                                                        start_date_IN,
                                                        end_date_IN,
                                                        notes_IN )
        
        instance_OUT = archive_instance
        return instance_OUT
        
    #-- END class method get_archive_instance() --#


    def get_PHNP_newspaper( self ):
        
        '''
        Instance must have paper_identifier set.  If set, start and end year and
            source and destination paths will also be stored.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "get_PHNP_newspaper"
        
        # if instance set, just return it.
        if ( self.phnp_newspaper is not None ):
        
            # already set.  Use it.
            instance_OUT = self.phnp_newspaper
            
        else:
        
            # not already set.  Create, then return.        
            instance_OUT = self.create_PHNP_newspaper()
            
        #-- END check if instance already nested. --#

        return instance_OUT
        
    #-- END method get_PHNP_newspaper() --#
    

    def initialize_from_database( self, paper_identifier_IN ):
        
        '''
        Instance must have paper_identifier set.  If set, start and end year and
            source and destination paths will also be stored.
        '''
        
        # return reference
        instance_OUT = None
        
        # declare variables
        me = "initialize_from_database"
        log_message = None
        paper_qs = None
        paper_count = -1
        phnp_newspaper_instance = None
        paper_identifier = None
        start_year = None
        end_year = None
        compressed_folder_path = None
        uncompressed_folder_path = None
        newspaper = None
        notes = None
                
        # try to retrieve from database
        paper_qs = Proquest_HNP_Newspaper.objects.filter( paper_identifier = paper_identifier_IN )
        paper_count = paper_qs.count()
        
        # anything returned?
        if ( paper_count == 1 ):
        
            # get instance
            phnp_newspaper_instance = paper_qs.get()

            # get needed information
            paper_identifier = phnp_newspaper_instance.paper_identifier
            start_year = phnp_newspaper_instance.start_year
            end_year = phnp_newspaper_instance.end_year
            compressed_folder_path = phnp_newspaper_instance.compressed_folder_path
            uncompressed_folder_path = phnp_newspaper_instance.uncompressed_folder_path
            newspaper = phnp_newspaper_instance.newspaper
            
            # store in self
            self.paper_identifier = paper_identifier_IN
            self.paper_start_year = start_year
            self.paper_end_year = end_year
            self.source_paper_path = compressed_folder_path
            self.destination_paper_path = uncompressed_folder_path
            self.phnp_newspaper = phnp_newspaper_instance
            self.newspaper = phnp_newspaper_instance.newspaper
            
        else:
            
            log_message = "In {}: ERROR - no Proquest_HNP_Newspaper record exists for paper_identifier \"{}\".  Returning None.".format( me, paper_identifier )
            self.output_debug_message( log_message, do_print_IN = True )
            phnp_newspaper_instance = None
            
        #-- END check if exists --#
            
        # return
        instance_OUT = phnp_newspaper_instance
        return instance_OUT
        
    #-- END method initialize_from_database() --#
    

    def make_dest_paper_folder( self ):
        
        # return reference
        did_it_exist_OUT = False
        
        # declare variables
        uncompressed_paper_path = None
        did_uncomp_paper_folder_exist = False
        log_message = None
        
        # get uncompressed paper path
        uncompressed_paper_path = self.destination_paper_path
        
        # check if uncompressed paper folder exists.
        if not os.path.exists( uncompressed_paper_path ):
            
            # no.  Make it.
            os.makedirs( uncompressed_paper_path )
            did_uncomp_paper_folder_exist = False
            log_message = "CREATED - Uncompressed paper folder {}".format( uncompressed_paper_path )
            self.output_debug_message( log_message, do_print_IN = True )
            
        else:
            
            # yes.  Set flag.
            did_uncomp_paper_folder_exist = True
            log_message = "EXISTS - Uncompressed paper folder {}".format( uncompressed_paper_path )
            self.output_debug_message( log_message, do_print_IN = True )
            
        #-- END check to see if paper folder exists. --#
        
        self.did_destination_paper_path_exist = did_uncomp_paper_folder_exist
        did_it_exist_OUT = did_uncomp_paper_folder_exist

        return did_it_exist_OUT
        
    #-- END method make_dest_paper_folder() --#
    

    def map_archive_folder_files_to_types( self, archive_path_IN = None, print_logging_IN = True ):
 
        # return reference
        type_to_file_path_map_OUT = None
        
        # declare variables
        me = "map_archive_folder_files_to_types"
        uncompressed_archive_path = None
        xml_file_list = None
        xml_file_path = None
        xml_file = None
        xml_dict = None
        xml_file_counter = None
        record_node = None
        object_type_node = None
        object_type_list = None
        object_type = None
        
        # declare variables - auditing
        xml_file_counter = None
        no_record_counter = None
        no_object_type_counter = None
        no_object_type_text_counter = None
        
        # output
        object_type_to_file_path_map = {}
        object_type_list = None
        file_path_list = None
        file_path_list_count = None
        file_path_example_list = None
        
        # get uncompressed archive path
        uncompressed_archive_path = archive_path_IN
        if ( ( uncompressed_archive_path is not None ) and ( uncompressed_archive_path != "" ) ):
        
            # loop over files in the current archive folder path.
            
            # get file list.
            xml_file_list = glob.glob( "{}/*.xml".format( uncompressed_archive_path ) )
            xml_file_count = len( xml_file_list )
        
            log_message = "Processing {} XML files in {}".format( xml_file_count, uncompressed_archive_path )
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
            
            # log the count
            log_message = "----> XML file count: {}".format( xml_file_count )
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
                    
            # loop
            xml_file_counter = 0
            no_record_counter = 0
            no_object_type_counter = 0
            no_object_type_text_counter = 0
            for xml_file_path in xml_file_list:
                
                xml_file_counter += 1
                
                # try to parse the file
                with open( xml_file_path ) as xml_file:
                
                    # parse XML
                    xml_dict = xmltodict.parse( xml_file.read() )
                    
                    # get root.Record.ObjectType value
                    record_node = xml_dict.get( "Record", None )
                    
                    if ( record_node is not None ):
                        
                        # get object type (looks like xmltodict stores
                        #     elements with no attributes and no child
                        #     elements just as a string contents mapped
                        #     to name in parent, no dictionary)
                        #
                        # so for:
                        # <Record>
                        #     ...
                        #     <ObjectType>Advertisement</ObjectType>
                        #     ...
                        # </Record>
                        #
                        # to get value:
                        #     record_node = xml_dict.get( "Record", None )
                        #     object_type_list = record_node.get( "ObjectType", None )
                        #     object_type = "|".join( object_type_list )
                        #
                        # NOT:
                        #     record_node = xml_dict.get( "Record", None )
                        #     object_type_node = record_node.get( "ObjectType", None )
                        #     object_type = object_type_node.get( "#text", None )
                        #
                        # Doc that led me astray: https://docs.python-guide.org/scenarios/xml/
                        object_type_list = record_node.get( "ObjectType", None )
                        object_type = "|".join( object_type_list )
            
                        # got a type?
                        if ( ( object_type is not None ) and ( object_type != "" ) ):
            
                            # we do.  Add path to appropriate list.
                            file_path_list = object_type_to_file_path_map.get( object_type, [] )
                            if ( xml_file_path not in file_path_list ):
                                
                                # not in list, add it.
                                file_path_list.append( xml_file_path )
                                
                            #-- END check to see if file path in list. --#
                                
                            object_type_to_file_path_map[ object_type ] = file_path_list
            
                        else:
            
                            # object type is None
                            no_object_type_text_counter += 1
            
                        #-- END check for type value --#
                        
                    else:
                        
                        # increment counter
                        no_record_counter += 1
                        
                    #-- END check if we found a "Record" node in root --#
            
                #-- END with open( xml_file_path )...: --#
                
            #-- END loop over XML files --#
            
            log_message = "\nIn {}:".format( me )
            log_message += "\nXML file count: {}".format( len( xml_file_list ) )
            log_message += "\nCounters:"
            log_message += "\n- Processed {} files".format( xml_file_counter )
            log_message += "\n- No Record: {}".format( no_record_counter )
            log_message += "\n- No ObjectType: {}".format( no_object_type_counter )
            log_message += "\n- No ObjectType value: {}".format( no_object_type_text_counter )
            log_message += "\n\nObjectType values and occurrence counts:"
            object_type_list = list( six.iterkeys( object_type_to_file_path_map ) )
            object_type_list.sort()
            for object_type in object_type_list:
                
                # get file path list
                file_path_list = object_type_to_file_path_map.get( object_type, [] )
                
                # print type and count
                file_path_list_count = len( file_path_list )
                file_path_example_list = file_path_list[ : 10 ]
                log_message += "\n- {} - {} files:".format( object_type, file_path_list_count )
                for file_path in file_path_example_list:
                    
                    log_message += "\n    - {}".format( file_path )
                    
                #-- END loop over example file paths. --#
                
            #-- END loop over object types. --#
            
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
        
        else:
        
            log_message = "In {}: ERROR - no path passed in, can't process.".format( me )
            self.output_debug_message( log_message, do_print_IN = True )
        
        #-- END check to see if path passed in. --#

        # return the map.        
        type_to_file_path_map_OUT = object_type_to_file_path_map
        
        return type_to_file_path_map_OUT

    #-- END method map_archive_folder_files_to_types() --#
    


    def process_archive_object_types( self, archive_path_IN = None, print_logging_IN = True ):
        
        # return reference
        object_type_to_count_map_OUT = None
        
        # declare variables
        me = "process_archive_object_types"
        archive_summary_dict = None
        
        # summarize archive
        archive_summary_dict = self.summarize_archive_files( archive_path_IN, print_logging_IN )
        
        # pull out type-to-count map
        object_type_to_count_map_OUT = archive_summary_dict.get( self.ARCHIVE_SUMMARY_TYPE_TO_COUNT_MAP, None )

        return object_type_to_count_map_OUT
                
    #-- END method process_archive_object_types() --#
        

    def process_paper_object_types( self, print_archive_logging_IN = False ):
        
        # return reference
        object_type_to_count_map_OUT = None
        
        # declare variables
        object_type_to_count_map = None
        uncompressed_paper_path = None
        
        # declare variables - folders
        xml_folder_list = None
        xml_folder_path = None
        xml_folder_count = None
        xml_folder_counter = None
        xml_folder_start_time = None
        xml_folder_end_time = None
        xml_folder_duration = None
        
        # declare variables - object types per folder
        object_type_value = None
        object_type_count = None
        folder_type_to_count_map = None
        folder_object_type_value = None
        folder_object_type_count = None
        
        # declare variables - update database
        paper_instance = None
        object_type_instance = None
        paper_type_qs = None
        paper_type_count = None
        paper_type_instance = None
        
        # declare variables - auditing
        start_dt = None
        end_dt = None
        duration = None
        
        # first, get paper path from instance.
        uncompressed_paper_path = self.destination_paper_path
        if ( ( uncompressed_paper_path is not None ) and ( uncompressed_paper_path != "" ) ):
        
            # init
            object_type_to_count_map = {}
            start_dt = datetime.datetime.now()
            
            # first, get the list of folders for the current paper.
            xml_folder_list = glob.glob( "{}/*".format( uncompressed_paper_path ) )
            xml_folder_count = len( xml_folder_list )
            
            log_message = "Processing {} XML folders in {}".format( xml_folder_count, uncompressed_paper_path )
            self.output_debug_message( log_message, do_print_IN = True )
            
            # loop over the folders
            xml_folder_counter = 0
            for xml_folder_path in xml_folder_list:
                
                xml_folder_counter += 1
                
                # log the folder
                xml_folder_start_time = datetime.datetime.now()
                log_message = "==> Processing XML folder {} ( {} of {} ) @ {}".format( xml_folder_path, xml_folder_counter, xml_folder_count, xml_folder_start_time )
                self.output_debug_message( log_message, do_print_IN = True )
                
                # call the method to process the object types in the folder
                folder_type_to_count_map = self.process_archive_object_types( xml_folder_path, print_archive_logging_IN )
                
                # merge results with main map.
                for folder_object_type_value, folder_object_type_count in six.iteritems( folder_type_to_count_map ):
                
                    # get count for this type from the master map.
                    object_type_count = object_type_to_count_map.get( folder_object_type_value, 0 )
                    
                    # add the count from the folder.
                    object_type_count += folder_object_type_count
                    
                    # place back into master map
                    object_type_to_count_map[ folder_object_type_value ] = object_type_count
                
                #-- END loop over results. --#
                
                # log the folder
                xml_folder_end_time = datetime.datetime.now()
                xml_folder_duration = xml_folder_end_time - xml_folder_start_time
                log_message = "----> Processing complete @ {} ( duration {} )\n".format( xml_folder_end_time, xml_folder_duration )
                self.output_debug_message( log_message, do_print_IN = True )
            
            #-- END loop over XML directories --#
            
        else:
        
            log_message = "In {}: ERROR - no folder path found, can't process.".format( me )
            self.output_debug_message( log_message, do_print_IN = True )

        #-- END check to see if paper path --#
            
        log_message = "XML folder count: {}".format( xml_folder_counter )
        self.output_debug_message( log_message, do_print_IN = True )
        
        log_message = "\nObjectType values and occurrence counts:"
        self.output_debug_message( log_message, do_print_IN = True )

        # loop over object type to count map
        for object_type, object_type_count in six.iteritems( object_type_to_count_map ):
        
            # print type and count
            log_message = "- {}: {}".format( object_type, object_type_count )
            self.output_debug_message( log_message, do_print_IN = True )
        
            # look up object type instance
            paper_instance = self.get_PHNP_newspaper()
            object_type_instance = self.fetch_object_type_instance( object_type )
        
            # see if already tied to paper
            paper_type_qs = paper_instance.phnp_newspaper_object_type_set.all()
            paper_type_qs = paper_type_qs.filter( proquest_hnp_object_type = object_type_instance )
            paper_type_count = paper_type_qs.count()
            if ( paper_type_count == 0 ):
            
                # not created yet.  Create it now.
                paper_type_instance = PHNP_Newspaper_Object_Type()
                paper_type_instance.proquest_hnp_newspaper = paper_instance
                paper_type_instance.proquest_hnp_object_type = object_type_instance
                paper_type_instance.item_count = object_type_count
                paper_type_instance.save()
                
            else:
            
                # ! TODO - should I update count?  Probably not.
                pass
                
            #-- END check to see if associated. --#
            
        #-- END loop over object types --#
        
        # timing
        end_dt = datetime.datetime.now()
        duration = end_dt - start_dt
        log_message = "Processing complete @ {} ( started at {}; duration: {} )\n".format( end_dt, start_dt, duration )
        self.output_debug_message( log_message, do_print_IN = True )

        object_type_to_count_map_OUT = object_type_to_count_map
        return object_type_to_count_map_OUT
                
    #-- END method process_archive_object_types() --#
        

    def summarize_archive_files( self, archive_path_IN = None, print_logging_IN = True ):
        
        # return reference
        summary_dict_OUT = None
        
        # declare variables
        me = "summarize_archive_files"
        log_message = None
        uncompressed_archive_path = None
        archive_path_item_list = None
        archive_identifier = None
        xml_file_list = None
        xml_file_count = None
        xml_file_path = None
        xml_file = None
        xml_dict = None
        xml_file_counter = None
        
        # declare variables - within XML file
        object_type_to_count_map = None
        object_type_count = None
        record_node = None
        object_type_node = None
        object_type_list = None
        object_type = None
        numeric_pub_date_list = None
        numeric_pub_date = None
        numeric_pub_date_int = None
        
        # declare variables - summary information
        min_pub_date_int = None
        min_pub_date = None
        max_pub_date_int = None
        max_pub_date = None
        archive_instance = None
                
        # declare variables - auditing
        xml_file_counter = None
        no_record_counter = None
        no_object_type_counter = None
        no_object_type_text_counter = None
        
        # declare variables - update database
        object_type_instance = None
        compressed_paper_path = None
        compressed_file_path = None
        archive_instance = None
        archive_type_qs = None
        archive_type_count = None
        archive_type_instance = None
        
        # get uncompressed archive path
        uncompressed_archive_path = archive_path_IN
        archive_path_item_list = uncompressed_archive_path.split( "/" )
        archive_identifier = archive_path_item_list[ -1 ]
        if ( ( uncompressed_archive_path is not None ) and ( uncompressed_archive_path != "" ) ):
        
            # init
            summary_dict_OUT = {}
            object_type_to_count_map = {}
            
            # get file list.
            xml_file_list = glob.glob( "{}/*.xml".format( uncompressed_archive_path ) )
            xml_file_count = len( xml_file_list )
        
            log_message = " In {}: Processing {} XML files in {}".format( me, xml_file_count, uncompressed_archive_path )
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
            
            # log the count
            log_message = "----> XML file count: {}".format( xml_file_count )
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
        
            # loop
            xml_file_counter = 0
            no_record_counter = 0
            no_object_type_counter = 0
            no_object_type_text_counter = 0
            min_pub_date_int = None
            max_pub_date_int = None
            for xml_file_path in xml_file_list:
                
                xml_file_counter += 1
                
                # try to parse the file
                with open( xml_file_path ) as xml_file:
                
                    # parse XML
                    xml_dict = xmltodict.parse( xml_file.read() )
                    
                    # get root.Record.ObjectType value
                    record_node = xml_dict.get( "Record", None )
                    
                    if ( record_node is not None ):
                        
                        # get object type (looks like xmltodict stores
                        #     elements with no attributes and no child
                        #     elements just as a string contents mapped
                        #     to name in parent, no dictionary)
                        #
                        # so for:
                        # <Record>
                        #     ...
                        #     <ObjectType>Advertisement</ObjectType>
                        #     ...
                        # </Record>
                        #
                        # to get value:
                        #     record_node = xml_dict.get( "Record", None )
                        #     object_type_list = record_node.get( "ObjectType", None )
                        #     object_type = "|".join( object_type_list )
                        #
                        # NOT:
                        #     record_node = xml_dict.get( "Record", None )
                        #     object_type_node = record_node.get( "ObjectType", None )
                        #     object_type = object_type_node.get( "#text", None )
                        #
                        # Doc that led me astray: https://docs.python-guide.org/scenarios/xml/
                        object_type_list = record_node.get( "ObjectType", None )
                        object_type = "|".join( object_type_list )
            
                        # got a type?
                        if ( ( object_type is not None ) and ( object_type != "" ) ):
            
                            # we do.  Increment count.
                            object_type_count = object_type_to_count_map.get( object_type, 0 )
                            object_type_count += 1
                            object_type_to_count_map[ object_type ] = object_type_count
            
                        else:
            
                            # object type is None
                            no_object_type_text_counter += 1
            
                        #-- END check for type value --#
                        
                        # get NumericPubDate
                        numeric_pub_date_list = record_node.get( "NumericPubDate", None )
                        numeric_pub_date = "".join( numeric_pub_date_list )
                        numeric_pub_date_int = int( numeric_pub_date )
                        
                        # is it largest...
                        if ( ( max_pub_date_int is None ) or ( numeric_pub_date_int > max_pub_date_int ) ):
                        
                            # either max is empty, or largest thus far.
                            max_pub_date_int = numeric_pub_date_int
                            
                        #-- END check to see if max --#                            

                        # ...or smallest?
                        if ( ( min_pub_date_int is None ) or ( numeric_pub_date_int < min_pub_date_int ) ):
                        
                            # either min is empty, or smallest thus far.
                            min_pub_date_int = numeric_pub_date_int
                            
                        #-- END check to see if min --#                                                

                    else:
                        
                        # increment counter
                        no_record_counter += 1
                        
                    #-- END check if we found a "Record" node in root --#
            
                #-- END with open( xml_file_path )...: --#
                
            #-- END loop over XML files --#
            
            log_message = "\nCounters:"
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
            log_message = "- Processed {} files".format( xml_file_counter )
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
            log_message = "- No Record: {}".format( no_record_counter )
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
            log_message = "- No ObjectType: {}".format( no_object_type_counter )
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
            log_message = "- No ObjectType value: {}".format( no_object_type_text_counter )
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
            log_message = "\nObjectType values and occurrence counts:"
            self.output_debug_message( log_message, do_print_IN = print_logging_IN )
            for object_type, object_type_count in six.iteritems( object_type_to_count_map ):
                
                # print type and count
                log_message = "- {}: {}".format( object_type, object_type_count )
                self.output_debug_message( log_message, do_print_IN = print_logging_IN )
                
            #-- END loop over object types. --#
            
        else:
        
            log_message = "In {}: ERROR - no path passed in, can't process.".format( me )
            self.output_debug_message( log_message, do_print_IN = True )
        
        #-- END check to see if path passed in. --#
        
        # store information in summary
        summary_dict_OUT[ self.ARCHIVE_SUMMARY_TYPE_TO_COUNT_MAP ] = object_type_to_count_map
        summary_dict_OUT[ self.ARCHIVE_SUMMARY_MIN_PUB_DATE ] = min_pub_date_int
        summary_dict_OUT[ self.ARCHIVE_SUMMARY_MAX_PUB_DATE ] = max_pub_date_int
        summary_dict_OUT[ self.ARCHIVE_SUMMARY_INSTANCE ] = None
        
        # get archive instance
        min_pub_date = str( min_pub_date_int )
        min_pub_date = datetime.datetime.strptime( min_pub_date, self.DATETIME_FORMAT_NUMERAL_PUB_DATE )
        max_pub_date = str( max_pub_date_int )
        max_pub_date = datetime.datetime.strptime( max_pub_date, self.DATETIME_FORMAT_NUMERAL_PUB_DATE )

        compressed_paper_path = self.source_paper_path
        if ( ( compressed_paper_path is not None ) and ( compressed_paper_path != "" ) ):
        
            compressed_file_path = "{}/{}.zip".format( compressed_paper_path, archive_identifier )
            
        else:
        
            compressed_file_path = None
        
        #-- END check to see if we have compressed paper path --#
        
        archive_instance = self.get_archive_instance( archive_identifier,
                                                      compressed_file_path_IN = compressed_file_path,
                                                      uncompressed_folder_path_IN = uncompressed_archive_path,
                                                      start_date_IN = min_pub_date,
                                                      end_date_IN = max_pub_date)

        # update it
        archive_instance.start_date = min_pub_date
        archive_instance.end_date = max_pub_date
        archive_instance.save()
        
        # loop over object type to count map
        for object_type, object_type_count in six.iteritems( object_type_to_count_map ):
        
            # look up object type instance
            object_type_instance = self.fetch_object_type_instance( object_type )
        
            # see if already tied to archive
            archive_type_qs = archive_instance.phnp_newspaper_archive_object_type_set.all()
            archive_type_qs = archive_type_qs.filter( proquest_hnp_object_type = object_type_instance )
            archive_type_count = archive_type_qs.count()
            if ( archive_type_count == 0 ):
            
                # not created yet.  Create it now.
                archive_type_instance = PHNP_Newspaper_Archive_Object_Type()
                archive_type_instance.proquest_hnp_newspaper_archive = archive_instance
                archive_type_instance.proquest_hnp_object_type = object_type_instance
                archive_type_instance.item_count = object_type_count
                archive_type_instance.save()
                
            else:
            
                # ! TODO - should I update count?  Probably not.
                pass
                
            #-- END check to see if associated. --#
            
        #-- END loop over object types --#
        
        # add to dict
        summary_dict_OUT[ self.ARCHIVE_SUMMARY_INSTANCE ] = archive_instance        

        return summary_dict_OUT
                
    #-- END method summarize_archive_files() --#
        

    def uncompress_paper_zip_files( self ):
    
        # declare variables - papers
        did_uncomp_paper_folder_exist = None
        
        # declare variables archive (.zip) files.
        me = "uncompress_paper_zip_files"
        source_paper_path = None
        uncompressed_paper_path = None
        zip_file_list = None
        zip_file_path = None
        zip_file_path_parts_list = None
        zip_file_name = None
        zip_file_name_parts_list = None
        archive_identifier = None
        uc_archive_folder_path = None
        zip_file = None
        
        # declare variables - auditing (uc = uncompressed)
        archive_file_counter = None
        did_uc_archive_folder_exist = None
        uc_folder_exists_counter = None
        start_dt = None
        end_dt = None
        time_delta = None
        
        # get source paper path and output paper path.
        source_paper_path = self.source_paper_path
        if ( ( source_paper_path is not None ) and ( source_paper_path != "" ) ):

            # get destination paper path
            uncompressed_paper_path = self.destination_paper_path
            if ( ( uncompressed_paper_path is not None ) and ( uncompressed_paper_path != "" ) ):
        
                # use glob to get list of zip files in paper source folder.
                zip_file_list = glob.glob( "{}/*.zip".format( source_paper_path ) )
                zip_file_count = len( zip_file_list )
                
                log_message = "==> zip file count: {}".format( zip_file_count )
                self.output_debug_message( log_message, do_print_IN = True )
                
                # loop over zip files.
                archive_file_counter = 0
                did_uc_archive_folder_exist = False
                uc_folder_exists_counter = 0
                for zip_file_path in zip_file_list:
                    
                    # increment counter
                    archive_file_counter += 1
                    
                    log_message = "----> processing file {} of {}".format( archive_file_counter, zip_file_count )
                    self.output_debug_message( log_message, do_print_IN = True )
                    
                    # get file name
                    
                    # split path into parts on path separator.
                    zip_file_path_parts_list = zip_file_path.split( "/" )
                
                    # file name is the last thing in the list.
                    zip_file_name = zip_file_path_parts_list[ -1 ]
                
                    # archive_identifier is name with ".zip" removed from end.
                    zip_file_name_parts_list = zip_file_name.split( ".zip" )
                    archive_identifier = zip_file_name_parts_list[ 0 ]
                    
                    # for now, log and print the things we've just created.
                    log_message = "==> path: {}".format( zip_file_path )
                    self.output_debug_message( log_message, do_print_IN = True )
                    log_message = "==> file: {}".format( zip_file_name )
                    self.output_debug_message( log_message, do_print_IN = True )
                    log_message = "==> ID: {}".format( archive_identifier )
                    self.output_debug_message( log_message, do_print_IN = True )
                
                    # check if uncompressed archive folder exists.
                    uc_archive_folder_path = "{}/{}".format( uncompressed_paper_path, archive_identifier )
                
                    log_message = "==> TO: {}".format( uc_archive_folder_path )
                    self.output_debug_message( log_message, do_print_IN = True )
                
                    # check if the uncompressed archive folder exists.
                    did_uc_archive_folder_exist = os.path.exists( uc_archive_folder_path )
                    if did_uc_archive_folder_exist == False:
                
                        # no.  Make it.
                        os.makedirs( uc_archive_folder_path )
                        log_message = "CREATED - Uncompressed archive folder {}".format( uc_archive_folder_path )
                        self.output_debug_message( log_message, do_print_IN = True )
                        
                        # and uncompress archive to it.
                        with zipfile.ZipFile( zip_file_path, 'r' ) as zip_file:
                
                            # starting extract.
                            start_dt = datetime.datetime.now()
                            log_message = "==> extract started at {}".format( start_dt )
                            self.output_debug_message( log_message, do_print_IN = True )
                            
                            # unzip to uncompressed archive folder path.
                            zip_file.extractall( uc_archive_folder_path )
                            
                            log_message = "EXTRACTED - {}".format( zip_file_path )
                            self.output_debug_message( log_message, do_print_IN = True )
                
                            log_message = "TO uncompressed archive folder - {}".format( uc_archive_folder_path )
                            self.output_debug_message( log_message, do_print_IN = True )
                            
                            # complete
                            end_dt = datetime.datetime.now()
                            
                            log_message = "==> extract completed at {}".format( end_dt )
                            self.output_debug_message( log_message, do_print_IN = True )
                            
                            log_message = "==> time elapsed: {}".format( end_dt - start_dt )
                            self.output_debug_message( log_message, do_print_IN = True )
                            
                        #-- END with ZipFile --#
                
                    else:
                
                        # yes.  Set flag.
                        uc_folder_exists_counter += 1
                        log_message = "EXISTS, so moving on - Uncompressed archive folder {}".format( uc_archive_folder_path )
                        self.output_debug_message( log_message, do_print_IN = True )
                
                    #-- END check to see if archive folder exists. --#
                
                    log_message = "------------------------------"
                    self.output_debug_message( log_message, do_print_IN = True )
                
                #-- END loop over zip files. --#
                
            else:
                    
                log_message = "In {}: no paper destination folder set in instance, so can't unzip.".format( me )
                self.output_debug_message( log_message, do_print_IN = True )
            
            #-- END check to see if we have a destination paper folder path --#
    
        else:
                
            log_message = "In {}: no paper source folder set in instance, so can't unzip.".format( me )
            self.output_debug_message( log_message, do_print_IN = True )
        
        #-- END check to see if we have a source paper folder path --#

    #-- END method uncompress_paper_zip_files() --#


#-- END class ProquestHNPNewspaperHelper --#