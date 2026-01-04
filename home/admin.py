from django.contrib import admin
from .models import Invitation, BusinessInquiry

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'business', 'role', 'created_at', 'get_is_used')
    list_filter = ('business', 'role', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('id', 'created_at', 'used_at', 'used_by')
    
    fieldsets = (
        ('Invitation', {
            'fields': ('id', 'email', 'business', 'role')
        }),
        ('Status', {
            'fields': ('get_is_used', 'created_at', 'used_at', 'used_by')
        }),
    )
    
    def get_is_used(self, obj):
        return obj.is_used
    get_is_used.boolean = True
    get_is_used.short_description = 'Used'


@admin.register(BusinessInquiry)
class BusinessInquiryAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'contact_name', 'email', 'num_locations', 'contacted', 'created_at')
    list_filter = ('contacted', 'created_at')
    search_fields = ('business_name', 'contact_name', 'email', 'phone')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Business Information', {
            'fields': ('business_name', 'contact_name', 'email', 'phone', 'num_locations')
        }),
        ('Inquiry Details', {
            'fields': ('message', 'created_at')
        }),
        ('Follow-up', {
            'fields': ('contacted', 'contacted_at', 'notes')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Auto-set contacted_at when contacted is marked True
        if obj.contacted and not obj.contacted_at:
            from django.utils import timezone
            obj.contacted_at = timezone.now()
        super().save_model(request, obj, form, change)
