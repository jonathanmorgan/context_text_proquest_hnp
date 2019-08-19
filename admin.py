from django.contrib import admin

# Import models
from context_text_proquest_hnp.models import Proquest_HNP_Object_Type
from context_text_proquest_hnp.models import Proquest_HNP_Object_Type_Raw_Value
from context_text_proquest_hnp.models import Proquest_HNP_Newspaper
from context_text_proquest_hnp.models import Proquest_HNP_Newspaper_Archive
from context_text_proquest_hnp.models import PHNP_Newspaper_Object_Type
from context_text_proquest_hnp.models import PHNP_Newspaper_Archive_Object_Type

# default admins
#admin.site.register( Proquest_HNP_Object_Type )
#admin.site.register( Proquest_HNP_Object_Type_Raw_Value )
#admin.site.register( Proquest_HNP_Newspaper )
#admin.site.register( Proquest_HNP_Newspaper_Archive )
#admin.site.register( PHNP_Newspaper_Object_Type )
#admin.site.register( PHNP_Newspaper_Archive_Object_Type )


#-------------------------------------------------------------------------------
# ! ==> Proquest_HNP_Object_Type Admin definition
#-------------------------------------------------------------------------------


class Proquest_HNP_Object_TypeAdmin( admin.ModelAdmin ):

    autocomplete_fields = [ 'parent_type' ]
    
    fieldsets = [
        (
            None,
            { 
                'fields' : [ 'raw_value', 'slug', 'name', 'parent_type', 'description', 'related_model' ]
            }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'id', 'raw_value', 'slug', 'name', 'last_modified' )
    #list_display_links = ( 'headline', )
    #list_filter = [ 'location' ]
    search_fields = [ 'slug', 'name', 'raw_value', 'description', 'id' ]
    #date_hierarchy = 'pub_date'
    ordering = [ "-last_modified" ]

#-- END Proquest_HNP_Object_TypeAdmin admin model --#

admin.site.register( Proquest_HNP_Object_Type, Proquest_HNP_Object_TypeAdmin )


#-------------------------------------------------------------------------------
# ! ==> Proquest_HNP_Object_Type Admin definition
#-------------------------------------------------------------------------------


class Proquest_HNP_Object_Type_Raw_ValueAdmin( admin.ModelAdmin ):

    autocomplete_fields = [ 'proquest_hnp_object_type' ]
    
    fieldsets = [
        (
            None,
            { 
                'fields' : [ 'proquest_hnp_object_type', 'raw_value' ]
            }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'id', 'proquest_hnp_object_type', 'raw_value' )
    #list_display_links = ( 'headline', )
    #list_filter = [ 'location' ]
    search_fields = [ 'raw_value', 'id' ]
    #date_hierarchy = 'pub_date'

#-- END Proquest_HNP_Object_Type_Raw_Value admin model --#

admin.site.register( Proquest_HNP_Object_Type_Raw_Value, Proquest_HNP_Object_Type_Raw_ValueAdmin )


#-------------------------------------------------------------------------------
# ! ==> Proquest_HNP_Newspaper_Archive admin definition
#-------------------------------------------------------------------------------


# type inline
class PHNPNA_PHNP_Newspaper_Archive_Object_TypeInline( admin.TabularInline ):

    # set up ajax-selects - for make_ajax_form, 1st argument is the model you
    #    are looking to make ajax selects form fields for; 2nd argument is a
    #    dict of pairs of field names in the model in argument 1 (with no quotes
    #    around them) mapped to lookup channels used to service them (lookup
    #    channels are defined in settings.py, implenented in a separate module -
    #    in this case, implemented in context.lookups.py
    #form = make_ajax_form( Entity_Relation_Type_Trait, dict( trait_type = 'trait_type' ) )
    autocomplete_fields = [ 'proquest_hnp_object_type' ]
    
    model = PHNP_Newspaper_Archive_Object_Type
    extra = 1
    fk_name = 'proquest_hnp_newspaper_archive'

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'proquest_hnp_object_type', 'item_count' ]
            }
        ),
        #(
        #    "More Detail (optional)",
        #    {
        #        'fields' : [ 'notes' ],
        #        'classes' : ( "collapse", )
        #    }
        #),
    ]

    ordering = [ 'proquest_hnp_object_type__raw_value' ]

#-- END class PHNPN_PHNP_Newspaper_Object_TypeInline --#


class Proquest_HNP_Newspaper_ArchiveAdmin( admin.ModelAdmin ):

    autocomplete_fields = [ 'proquest_hnp_newspaper' ]

    fieldsets = [
        (
            None,
            { 
                'fields' : [ 'proquest_hnp_newspaper', 'archive_identifier', 'start_date', 'end_date', 'compressed_file_path', 'uncompressed_folder_path' ]
            },
        ),
        (
            "More details (Optional)",
            {
                "fields" : [ "notes" ],
                "classes" : ( "collapse", )
            }
        ),
    ]

    inlines = [
        PHNPNA_PHNP_Newspaper_Archive_Object_TypeInline,
    ]

    list_display = ( 'id', 'proquest_hnp_newspaper', 'archive_identifier', 'start_date', 'end_date' )
    list_display_links = ( 'id', 'archive_identifier' )
    list_filter = [ 'proquest_hnp_newspaper' ]
    search_fields = [ 'archive_identifier', 'start_date', 'end_date', 'compressed_file_path', 'uncompressed_folder_path', 'id' ]
    #date_hierarchy = 'pub_date'

#-- END Entity_TypeAdmin admin model --#

admin.site.register( Proquest_HNP_Newspaper_Archive, Proquest_HNP_Newspaper_ArchiveAdmin )


#-------------------------------------------------------------------------------
# ! ==> Proquest_HNP_Newspaper admin definition
#-------------------------------------------------------------------------------


# type inline
class PHNPN_PHNP_Newspaper_Object_TypeInline( admin.TabularInline ):

    # set up ajax-selects - for make_ajax_form, 1st argument is the model you
    #    are looking to make ajax selects form fields for; 2nd argument is a
    #    dict of pairs of field names in the model in argument 1 (with no quotes
    #    around them) mapped to lookup channels used to service them (lookup
    #    channels are defined in settings.py, implenented in a separate module -
    #    in this case, implemented in context.lookups.py
    #form = make_ajax_form( Entity_Relation_Type_Trait, dict( trait_type = 'trait_type' ) )
    autocomplete_fields = [ 'proquest_hnp_object_type' ]
    
    model = PHNP_Newspaper_Object_Type
    extra = 1
    fk_name = 'proquest_hnp_newspaper'

    fieldsets = [
        (
            None,
            {
                'fields' : [ 'proquest_hnp_object_type', 'item_count' ]
            }
        ),
        #(
        #    "More Detail (optional)",
        #    {
        #        'fields' : [ 'notes' ],
        #        'classes' : ( "collapse", )
        #    }
        #),
    ]

#-- END class PHNPN_PHNP_Newspaper_Object_TypeInline --#


class Proquest_HNP_NewspaperAdmin( admin.ModelAdmin ):

    autocomplete_fields = [ 'newspaper' ]

    fieldsets = [
        (
            None,
            { 
                'fields' : [ 'paper_identifier', 'start_year', 'end_year', 'compressed_folder_path', 'uncompressed_folder_path', 'archive_file_name_prefix', 'newspaper' ]
            },
        ),
        (
            "More details (Optional)",
            {
                "fields" : [ "notes" ],
                "classes" : ( "collapse", )
            }
        ),
    ]

    inlines = [
        PHNPN_PHNP_Newspaper_Object_TypeInline,
    ]

    list_display = ( 'id', 'paper_identifier', 'start_year', 'end_year' )
    list_display_links = ( 'id', 'paper_identifier' )
    #list_filter = [ 'location' ]
    search_fields = [ 'paper_identifier', 'start_year', 'end_year', 'compressed_folder_path', 'uncompressed_folder_path', 'archive_file_name_prefix', 'notes', 'id' ]
    #date_hierarchy = 'pub_date'

#-- END Entity_TypeAdmin admin model --#

admin.site.register( Proquest_HNP_Newspaper, Proquest_HNP_NewspaperAdmin )


#-------------------------------------------------------------------------------
# ! ==> PHNP_Newspaper_Object_Type Admin definition
#-------------------------------------------------------------------------------


class PHNP_Newspaper_Object_TypeAdmin( admin.ModelAdmin ):

    autocomplete_fields = [ 'proquest_hnp_newspaper', 'proquest_hnp_object_type' ]
    
    fieldsets = [
        (
            None,
            { 
                'fields' : [ 'proquest_hnp_newspaper', 'proquest_hnp_object_type', 'item_count' ]
            }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'id', 'proquest_hnp_newspaper', 'proquest_hnp_object_type', 'item_count' )
    #list_display_links = ( 'headline', )
    #list_filter = [ 'location' ]
    search_fields = [ 'item_count', 'id' ]
    #date_hierarchy = 'pub_date'

#-- END Proquest_HNP_Object_TypeAdmin admin model --#

admin.site.register( PHNP_Newspaper_Object_Type, PHNP_Newspaper_Object_TypeAdmin )


#-------------------------------------------------------------------------------
# ! ==> PHNP_Newspaper_Archive_Object_Type Admin definition
#-------------------------------------------------------------------------------


class PHNP_Newspaper_Archive_Object_TypeAdmin( admin.ModelAdmin ):

    autocomplete_fields = [ 'proquest_hnp_newspaper_archive', 'proquest_hnp_object_type' ]
    
    fieldsets = [
        (
            None,
            { 
                'fields' : [ 'proquest_hnp_newspaper_archive', 'proquest_hnp_object_type', 'item_count' ]
            }
        ),
    ]

    #inlines = [
    #    Source_OrganizationInline,
    #]

    list_display = ( 'id', 'proquest_hnp_newspaper_archive', 'proquest_hnp_object_type', 'item_count' )
    #list_display_links = ( 'headline', )
    list_filter = [ 'proquest_hnp_newspaper_archive__proquest_hnp_newspaper', 'proquest_hnp_object_type' ]
    search_fields = [ 'item_count', 'id' ]
    #date_hierarchy = 'pub_date'

#-- END Proquest_HNP_Object_TypeAdmin admin model --#

admin.site.register( PHNP_Newspaper_Archive_Object_Type, PHNP_Newspaper_Archive_Object_TypeAdmin )


