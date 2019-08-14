from django.contrib import admin

# Import models
from context_text_proquest_hnp.models import Proquest_HNP_Object_Type
from context_text_proquest_hnp.models import Proquest_HNP_Newspaper
from context_text_proquest_hnp.models import Proquest_HNP_Newspaper_Archive
from context_text_proquest_hnp.models import PHNP_Newspaper_Object_Type
from context_text_proquest_hnp.models import PHNP_Newspaper_Archive_Object_Type

# default admins
admin.site.register( Proquest_HNP_Object_Type )
admin.site.register( Proquest_HNP_Newspaper )
admin.site.register( Proquest_HNP_Newspaper_Archive )
admin.site.register( PHNP_Newspaper_Object_Type )
admin.site.register( PHNP_Newspaper_Archive_Object_Type )
