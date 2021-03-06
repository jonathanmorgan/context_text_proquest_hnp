from __future__ import unicode_literals
from __future__ import division

'''
Copyright 2019 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/context_text_proquest_hnp.

context_text_proquest_hnp is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

context_text_proquest_hnp is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with http://github.com/jonathanmorgan/context_text_proquest_hnp. If not, see http://www.gnu.org/licenses/.
'''


#===============================================================================
# ! ==> Imports
#===============================================================================

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible

# taggit tagging APIs
from taggit.managers import TaggableManager

# context imports
from context.models import Abstract_Context_With_JSON
from context.models import Abstract_Type

# context_text imports
from context_text.models import Newspaper


#===============================================================================
# ! ==> Shared variables and functions
#===============================================================================

STATUS_SUCCESS = "Success!"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
BS_PARSER = "html5lib"

'''
Debugging code, shared across all models.
'''

DEBUG = True

def output_debug( message_IN, method_IN = "", indent_with_IN = "", logger_name_IN = "" ):
    
    '''
    Accepts message string.  If debug is on, logs it.  If not,
       does nothing for now.
    '''
    
    # declare variables
    my_message = ""
    my_logger = None
    my_logger_name = ""

    # got a message?
    if ( message_IN ):
    
        # only print if debug is on.
        if ( DEBUG == True ):
        
            my_message = message_IN
        
            # got a method?
            if ( method_IN ):
            
                # We do - append to front of message.
                my_message = "In " + method_IN + ": " + my_message
                
            #-- END check to see if method passed in --#
            
            # indent?
            if ( indent_with_IN ):
                
                my_message = indent_with_IN + my_message
                
            #-- END check to see if we indent. --#
        
            # debug is on.  Start logging rather than using print().
            #print( my_message )
            
            # got a logger name?
            my_logger_name = "context_text.models"
            if ( ( logger_name_IN is not None ) and ( logger_name_IN != "" ) ):
            
                # use logger name passed in.
                my_logger_name = logger_name_IN
                
            #-- END check to see if logger name --#
                
            # get logger
            my_logger = LoggingHelper.get_a_logger( my_logger_name )
            
            # log debug.
            my_logger.debug( my_message )
        
        #-- END check to see if debug is on --#
    
    #-- END check to see if message. --#

#-- END method output_debug() --#


def get_dict_value( dict_IN, name_IN, default_IN = None ):

    '''
    Convenience method for getting value for name of dictionary entry that might
       or might not exist in dictionary.
    '''
    
    # return reference
    value_OUT = default_IN

    # got a dict?
    if ( dict_IN ):
    
        # got a name?
        if ( name_IN ):

            # name in dictionary?
            if ( name_IN in dict_IN ):
            
                # yup.  Get it.
                value_OUT = dict_IN[ name_IN ]
                
            else:
            
                # no.  Return default.
                value_OUT = default_IN
            
            #-- END check to see if start date in arguments --#
            
        else:
        
            value_OUT = default_IN
            
        #-- END check to see if name passed in. --#
        
    else:
    
        value_OUT = default_IN
        
    #-- END check to see if dict passed in. --#

    return value_OUT

#-- END method get_dict_value() --#


#===============================================================================
# ! ==> Models
#===============================================================================


# Abstract_Type model
@python_2_unicode_compatible
class Proquest_HNP_Object_Type( Abstract_Type ):

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------


    slug = models.SlugField()
    #name = models.CharField( max_length = 255, blank = True, null = True )
    #related_model = models.CharField( max_length = 255, blank = True, null = True )
    #description = models.TextField( blank = True )
    parent_type = models.ForeignKey( "Proquest_HNP_Object_Type", on_delete = models.SET_NULL, blank = True, null = True )
    raw_value = models.TextField( unique = True )


    #----------------------------------------------------------------------
    # Meta
    #----------------------------------------------------------------------


    # Meta-data for this class.
    class Meta:

        ordering = [ 'raw_value' ]
        
    #-- END class Meta --#


    #----------------------------------------------------------------------
    # instance methods
    #----------------------------------------------------------------------


    def __init__( self, *args, **kwargs ):
        
        # call parent __init()__ first.
        super( Proquest_HNP_Object_Type, self ).__init__( *args, **kwargs )

    #-- END method __init__() --#


    def __str__( self ):
 
        # return reference
        string_OUT = ''
        
        # declare variables
        string_list = []
        
        # id
        if ( self.id is not None ):
        
            string_list.append( str( self.id ) )
            
        #-- END check to see if ID --#
        
        # got a slug?  (slimy)
        if ( ( self.slug is not None ) and ( self.slug != "" ) ):
        
            string_list.append( str( self.slug ) )
            
        #-- END check for slug. --#

        # got a name?
        if ( ( self.name is not None ) and ( self.name != "" ) ):
        
            string_list.append( str( self.name ) )
            
        #-- END check to see if name. --#
 
        string_OUT += " - ".join( string_list )
 
        return string_OUT

    #-- END method __str__() --#


    def set_raw_value( self, value_IN ):
        
        # return reference
        value_OUT = None
        
        # declare variables
        me = "set_raw_value"
        my_id = None
        my_slug = None
        my_raw_value = None
        cleaned_value = None
        raw_value_qs = None
        raw_value_count = None
        raw_value_instance = None
        
        # init
        my_id = self.id
        my_slug = self.slug
        my_raw_value = self.raw_value
        
        # got a value?
        if ( ( value_IN is not None ) and ( value_IN != "" ) ):
        
            value_OUT = value_IN
            
            # got a slug already?
            if ( ( my_slug is None ) or ( my_slug == "" ) ):
            
                # no slug - clean raw value for slugging.
                cleaned_value = value_IN.strip()
                cleaned_value = slugify( cleaned_value )
        
                # store slug.
                self.slug = cleaned_value
                
            #-- END check to see if slug --#
            
            # got an initial raw value already?
            if ( ( my_raw_value is None ) or ( my_raw_value == "" ) ):
            
                # no raw value, use this one.
                self.raw_value = value_IN
                
            #-- END check to see if slug --#
            
            # is this already in the database?
            if ( ( my_id is not None ) and ( my_id > 0 ) ):
            
                # already in database.  See if raw value is in overflow table
                #     set.  If not, add it using the model
                #     Proquest_HNP_Object_Type_Raw_Value.
                raw_value_qs = self.raw_value_set.all()
                raw_value_qs = raw_value_qs.filter( raw_value = value_IN )
                raw_value_count = raw_value_qs.count()
                if ( raw_value_count == 0 ):
                
                    # not a known synonym.  Add it.
                    raw_value_instance = Proquest_HNP_Object_Type_Raw_Value()
                    raw_value_instance.proquest_hnp_object_type = self
                    raw_value_instance.raw_value = value_IN
                    raw_value_instance.save()
                    
                else:
                
                    # known synonym, already in the database.  Move on.
                    pass
                    
                #-- END check to see if raw value already stored. --#                
            
            #-- END check to see if ID present --#    
            
        else:
        
            # nothing passed in, nothing to do.
            print( "IN {}: nothing passed in, nothing to do.".format( me ) )
            value_OUT = None

        #-- END check to see if value passed in. --#            

        return value_OUT

    #-- END method set_raw_value() --#

#-- END model Proquest_HNP_Object_Type --#


# Proquest_HNP_Object_Type_Raw_Value model
@python_2_unicode_compatible
class Proquest_HNP_Object_Type_Raw_Value( models.Model ):

    #----------------------------------------------------------------------
    # model fields and meta
    #----------------------------------------------------------------------


    proquest_hnp_object_type = models.ForeignKey( Proquest_HNP_Object_Type, on_delete = models.CASCADE, related_name = "raw_value_set" )
    raw_value = models.TextField()


    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # declare variables
        prefix_string = ""
        
        if ( self.id ):
        
            # yes. output.
            string_OUT += str( self.id )
            prefix_string = " - "

        #-- END check to see if ID --#

        if ( self.proquest_hnp_object_type ):
        
            string_OUT += "{}{}".format( prefix_string, self.proquest_hnp_object_type )
            prefix_string = " - "
            
        #-- END check to see if object type. --#
            
        if ( self.raw_value ):
        
            string_OUT += "{}{}".format( prefix_string, self.raw_value )
            prefix_string = " - "
            
        #-- END check to see if object type. --#
            
        return string_OUT
        
    #-- END method __str__() --#


#= End Proquest_HNP_Object_Type_Raw_Value Model ======================================================


# Proquest_HNP_Newspaper model
@python_2_unicode_compatible
class Proquest_HNP_Newspaper( models.Model ):

    paper_identifier = models.CharField( max_length = 255, unique = True )
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    compressed_folder_path = models.TextField( blank = True, null = True )
    uncompressed_folder_path = models.TextField( blank = True, null = True )
    archive_file_name_prefix = models.CharField( max_length = 255, blank = True, null = True  )
    newspaper = models.ForeignKey( Newspaper, on_delete = models.SET_NULL, blank = True, null = True )
    notes = models.TextField( blank = True, null = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # declare variables
        prefix_string = ""
        
        if ( self.id ):
        
            # yes. output.
            string_OUT += str( self.id )
            prefix_string = " - "

        #-- END check to see if ID --#

        if ( self.paper_identifier ):
        
            string_OUT += prefix_string + str( self.paper_identifier )
            prefix_string = " - "
            
        #-- END check to see if newspaper. --#
            
        if ( self.newspaper ):
        
            string_OUT += prefix_string + self.newspaper.name
            prefix_string = " - "
            
        #-- END check to see if newspaper. --#
            
        return string_OUT
        
    #-- END method __str__() --#


#= End Proquest_HNP_Newspaper Model ======================================================


# Proquest_HNP_Newspaper_Archive model
@python_2_unicode_compatible
class Proquest_HNP_Newspaper_Archive( models.Model ):

    proquest_hnp_newspaper = models.ForeignKey( Proquest_HNP_Newspaper, on_delete = models.CASCADE )
    archive_identifier = models.CharField( max_length = 255, unique = True )
    compressed_file_path = models.TextField( blank = True, null = True )
    uncompressed_folder_path = models.TextField( blank = True, null = True )    
    start_date = models.DateField( blank = True, null = True )
    end_date = models.DateField( blank = True, null = True )
    notes = models.TextField( blank = True, null = True )

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # declare variables
        prefix_string = ""
        
        if ( self.id ):
        
            # yes. output.
            string_OUT += str( self.id )
            prefix_string = " - "

        #-- END check to see if ID --#

        if ( self.archive_identifier ):
        
            string_OUT += "{}{}".format( prefix_string, self.archive_identifier )
            prefix_string = " - "
            
        #-- END check to see if archive_identifier. --#
            
        if ( self.proquest_hnp_newspaper ):
        
            string_OUT += "{}{}".format( prefix_string, self.proquest_hnp_newspaper.paper_identifier )
            prefix_string = " - "
            
        #-- END check to see if newspaper. --#
            
        if ( self.start_date ):
        
            string_OUT += "{} from {}".format( prefix_string, self.start_date )
            prefix_string = " - "
            
        #-- END check to see if start_date. --#
            
        if ( self.end_date ):
        
            string_OUT += "{} to {}".format( prefix_string, self.end_date )
            prefix_string = " - "
            
        #-- END check to see if end_date. --#
            
        return string_OUT
        
    #-- END method __str__() --#


#= End Proquest_HNP_Newspaper_Archive Model ======================================================


# PHNP_Newspaper_Object_Type model
@python_2_unicode_compatible
class PHNP_Newspaper_Object_Type( models.Model ):

    proquest_hnp_newspaper = models.ForeignKey( Proquest_HNP_Newspaper, on_delete = models.CASCADE )
    proquest_hnp_object_type = models.ForeignKey( Proquest_HNP_Object_Type, on_delete = models.CASCADE )
    item_count = models.IntegerField()

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # declare variables
        prefix_string = ""
        
        if ( self.id ):
        
            # yes. output.
            string_OUT += str( self.id )
            prefix_string = " - "

        #-- END check to see if ID --#

        if ( self.proquest_hnp_newspaper ):
        
            string_OUT += "{}{}".format( prefix_string, self.proquest_hnp_newspaper.paper_identifier )
            prefix_string = " - "
            
        #-- END check to see if proquest_hnp_newspaper. --#
            
        if ( self.proquest_hnp_object_type ):
        
            string_OUT += "{}{}".format( prefix_string, self.proquest_hnp_object_type )
            prefix_string = " - "
            
        #-- END check to see if object type. --#
            
        if ( self.item_count ):
        
            string_OUT += "{}{}".format( prefix_string, self.item_count )
            prefix_string = " - "
            
        #-- END check to see if object type. --#
            
        return string_OUT
        
    #-- END method __str__() --#


#= End PHNP_Newspaper_Object_Type Model ======================================================


# PHNP_Newspaper_Archive_Object_Type model
@python_2_unicode_compatible
class PHNP_Newspaper_Archive_Object_Type( models.Model ):

    proquest_hnp_newspaper_archive = models.ForeignKey( Proquest_HNP_Newspaper_Archive, on_delete = models.CASCADE )
    proquest_hnp_object_type = models.ForeignKey( Proquest_HNP_Object_Type, on_delete = models.CASCADE )
    item_count = models.IntegerField()

    #----------------------------------------------------------------------
    # methods
    #----------------------------------------------------------------------


    def __str__( self ):
        
        # return reference
        string_OUT = ""
        
        # declare variables
        prefix_string = ""
        
        if ( self.id ):
        
            # yes. output.
            string_OUT += str( self.id )
            prefix_string = " - "

        #-- END check to see if ID --#

        if ( self.proquest_hnp_newspaper_archive ):
        
            string_OUT += "{}{}".format( prefix_string, self.proquest_hnp_newspaper_archive.archive_identifier )
            prefix_string = " - "
            
        #-- END check to see if proquest_hnp_newspaper. --#
            
        if ( self.proquest_hnp_object_type ):
        
            string_OUT += "{}{}".format( prefix_string, self.proquest_hnp_object_type )
            prefix_string = " - "
            
        #-- END check to see if object type. --#
            
        if ( self.item_count ):
        
            string_OUT += "{}{}".format( prefix_string, self.item_count )
            prefix_string = " - "
            
        #-- END check to see if object type. --#
            
        return string_OUT
        
    #-- END method __str__() --#


#= End PHNP_Newspaper_Object_Type Model ======================================================

