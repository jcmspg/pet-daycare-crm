from django.contrib import admin
from .models import Business, Tutor, Pet, TrainingProgress

class PetPreviewInline(admin.TabularInline):
    model = Pet.tutors.through
    extra = 0
    fields = ['pet_name']
    readonly_fields = ['pet_name']
    
    def pet_name(self, obj):
        return obj.pet.name
    pet_name.short_description = 'Pet'

class PetBusinessPreviewInline(admin.TabularInline):
    model = Pet
    extra = 0
    fields = ['name_readonly', 'first_tutor_phone']
    readonly_fields = ['name_readonly', 'first_tutor_phone']
    
    def name_readonly(self, obj):
        return obj.name
    name_readonly.short_description = 'Pet Name'
    
    def first_tutor_phone(self, obj):
        if obj.tutors.exists():
            return obj.tutors.first().phone
        return '-'
    first_tutor_phone.short_description = 'Phone'

class TutorPreviewInline(admin.TabularInline):
    model = Tutor
    extra = 0
    fields = ['name_readonly']  # ← FIXED: removed pets_count
    readonly_fields = ['name_readonly']
    
    def name_readonly(self, obj):
        return obj.name
    name_readonly.short_description = 'Tutor Name'

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name', 'tutors_count', 'pets_count']
    inlines = [PetBusinessPreviewInline, TutorPreviewInline]
    
    def tutors_count(self, obj):
        return obj.tutors.count()
    tutors_count.short_description = 'Tutors'
    
    def pets_count(self, obj):
        return obj.pets.count()
    pets_count.short_description = 'Pets'

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ['name', 'business', 'pets_count']
    inlines = [PetPreviewInline]
    
    def pets_count(self, obj):
        return obj.pets.count()
    pets_count.short_description = 'Pets'

@admin.register(TrainingProgress)
class TrainingProgressAdmin(admin.ModelAdmin):
    list_display = ('pet', 'title', 'progress', 'date')
    search_fields = ('pet__name', 'title')
    list_filter = ('date',)

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ['name', 'business', 'tutors_list']
    filter_horizontal = ('tutors',)
    
    def tutors_list(self, obj):
        return ", ".join([t.name for t in obj.tutors.all()[:3]])
    tutors_list.short_description = 'Tutors'
