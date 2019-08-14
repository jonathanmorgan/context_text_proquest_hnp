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

# python_utilities
from python_utilities.parameters.param_container import ParamContainer
from python_utilities.rate_limited.basic_rate_limited import BasicRateLimited

# context_text
from context_text.shared.context_text_base import ContextTextBase

# context_text_proquest_hnp
from context_text_proquest_hnp.models import Proquest_HNP_Newspaper

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


    #-----------------------------------------------------------------------------
    # ! ==> class methods
    #-----------------------------------------------------------------------------


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
        
        # set logger name (for LoggingHelper parent class: (LoggingHelper --> BasicRateLimited --> ContextTextBase).
        self.set_logger_name( "context_text_proquest_hnp.proquest_hnp_newspaper" )
        
    #-- END method __init__() --#


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
        instance_OUT = phnp_newspaper_instance
        return instance_OUT
        
    #-- END method create_PHNP_newspaper() --#
    

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
        file_path_list = None
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
            for object_type, file_path_list in six.iteritems( object_type_to_file_path_map ):
                
                # print type and count
                file_path_example_list = file_path_list[ : 10 ]
                log_message += "\n- {}:".format( object_type )
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
        archive_summary_dict = summarize_archive_files( archive_path_IN, print_logging_IN )
        
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
        
        
        # first, get paper path from instance.
        uncompressed_paper_path = self.destination_paper_path
        if ( ( uncompressed_paper_path is not None ) and ( uncompressed_paper_path != "" ) ):
        
            # init
            object_type_to_count_map = {}
            
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

        for object_type, object_type_count in six.iteritems( object_type_to_count_map ):
            
            # print type and count
            log_message = "- {}: {}".format( object_type, object_type_count )
            self.output_debug_message( log_message, do_print_IN = True )
        
        #-- END loop over object types. --#

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
        numeric_pub_date = None
        numeric_pub_date_int = None
        
        # declare variables - summary information
        min_pub_date = None
        max_pub_date = None
                
        # declare variables - auditing
        xml_file_counter = None
        no_record_counter = None
        no_object_type_counter = None
        no_object_type_text_counter = None
        
        # get uncompressed archive path
        uncompressed_archive_path = archive_path_IN
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
            min_pub_date = None
            max_pub_date = None
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
                        numeric_pub_date = record_node.get( "NumericPubDate", None )
                        numeric_pub_date_int = int( numeric_pub_date )
                        
                        # is it largest...
                        if ( ( max_pub_date is None ) or ( numeric_pub_date_int > max_pub_date ) ):
                        
                            # either max is empty, or largest thus far.
                            max_pub_date = numeric_pub_date_int
                            
                        #-- END check to see if max --#                            

                        # ...or smallest?
                        if ( ( min_pub_date is None ) or ( numeric_pub_date_int < min_pub_date ) ):
                        
                            # either min is empty, or smallest thus far.
                            min_pub_date = numeric_pub_date_int
                            
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
        summary_dict_OUT[ self.ARCHIVE_SUMMARY_MIN_PUB_DATE ] = min_pub_date
        summary_dict_OUT[ self.ARCHIVE_SUMMARY_MAX_PUB_DATE ] = max_pub_date
        summary_dict_OUT[ self.ARCHIVE_SUMMARY_INSTANCE ] = None

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