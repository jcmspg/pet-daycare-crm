"""
Custom managers and querysets for business-scoped queries
"""
from django.db import models


class BusinessScopedQuerySet(models.QuerySet):
    """Base queryset that filters by business"""
    
    def for_business(self, business):
        """Filter queryset by business"""
        return self.filter(business=business)
    
    def active(self):
        """Filter for active records (if model has is_active field)"""
        if hasattr(self.model, 'is_active'):
            return self.filter(is_active=True)
        return self.all()


class PetQuerySet(BusinessScopedQuerySet):
    """Custom queryset for Pet model"""
    
    def for_business(self, business):
        """Filter pets by business"""
        return self.filter(business=business)
    
    def for_tutor(self, tutor):
        """Filter pets belonging to a tutor"""
        return self.filter(tutors=tutor)
    
    def with_related(self):
        """Prefetch related objects for performance"""
        return self.select_related('business').prefetch_related('tutors', 'service_bookings')


class PetManager(models.Manager):
    """Custom manager for Pet model"""
    
    def get_queryset(self):
        return PetQuerySet(self.model, using=self._db)
    
    def for_business(self, business):
        """Get pets for a specific business"""
        return self.get_queryset().for_business(business)
    
    def for_tutor(self, tutor):
        """Get pets belonging to a tutor"""
        return self.get_queryset().for_tutor(tutor)
    
    def with_related(self):
        """Get pets with related objects prefetched"""
        return self.get_queryset().with_related()


class TutorQuerySet(BusinessScopedQuerySet):
    """Custom queryset for Tutor model"""
    
    def for_business(self, business):
        """Filter tutors by business"""
        return self.filter(business=business)
    
    def with_pets(self):
        """Prefetch pets for tutors"""
        return self.prefetch_related('pets')


class TutorManager(models.Manager):
    """Custom manager for Tutor model"""
    
    def get_queryset(self):
        return TutorQuerySet(self.model, using=self._db)
    
    def for_business(self, business):
        """Get tutors for a specific business"""
        return self.get_queryset().for_business(business)
    
    def with_pets(self):
        """Get tutors with pets prefetched"""
        return self.get_queryset().with_pets()


class StaffQuerySet(BusinessScopedQuerySet):
    """Custom queryset for Staff model"""
    
    def for_business(self, business):
        """Filter staff by business"""
        return self.filter(business=business)
    
    def managers(self):
        """Filter for managers only"""
        return self.filter(role='manager')
    
    def regular_staff(self):
        """Filter for regular staff (non-managers)"""
        return self.filter(role='staff')
    
    def with_user(self):
        """Select related user for performance"""
        return self.select_related('user', 'business')


class StaffManager(models.Manager):
    """Custom manager for Staff model"""
    
    def get_queryset(self):
        return StaffQuerySet(self.model, using=self._db)
    
    def for_business(self, business):
        """Get staff for a specific business"""
        return self.get_queryset().for_business(business)
    
    def managers(self):
        """Get managers only"""
        return self.get_queryset().managers()
    
    def regular_staff(self):
        """Get regular staff only"""
        return self.get_queryset().regular_staff()
    
    def with_user(self):
        """Get staff with user prefetched"""
        return self.get_queryset().with_user()
