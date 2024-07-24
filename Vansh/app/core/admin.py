from django.contrib import admin
from .models import FamilyMember, Relationship

class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'gender', 'occupation')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('gender',)
    ordering = ('first_name', 'last_name')

class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('from_member', 'to_member', 'relationship_type', 'is_spouse')
    search_fields = ('from_member__first_name', 'from_member__last_name', 'to_member__first_name', 'to_member__last_name', 'relationship_type')
    list_filter = ('relationship_type', 'is_spouse')
    ordering = ('from_member', 'relationship_type', 'to_member', )
    
    # Optional: Inline Relationship management for easier editing
    # If you want to manage relationships inline within the FamilyMember admin
    # class RelationshipInline(admin.TabularInline):
    #     model = Relationship
    #     extra = 1
    
    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     # You can add additional filtering logic here if needed
    #     return queryset

admin.site.register(FamilyMember, FamilyMemberAdmin)
admin.site.register(Relationship, RelationshipAdmin)
