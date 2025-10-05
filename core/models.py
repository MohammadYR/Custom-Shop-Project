import uuid
from django.db import models
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())
    def alive(self):
        return self.filter(deleted_at__isnull=True)
    def dead(self):
        return self.exclude(deleted_at__isnull=True)
    def restore(self):
        return self.update(deleted_at=None)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)
    # def alive(self): 
    #     return self.get_queryset().alive()
    def dead(self):  
        # return self.model.all_objects.get_queryset().dead()
        return SoftDeleteQuerySet(self.model, using=self._db).dead()

class BaseModel(models.Model):
    """
    Abstract base model that implements UUID primary key, timestamping, and soft-delete behavior.
    Behavior and Methods
    - delete(self, using=None, keep_parents=False):
        Performs a soft-delete by setting deleted_at to the current time (if not already set)
        and saving the instance. This preserves the database row for potential restore or auditing.
    - hard_delete(self, using=None, keep_parents=False):
        Performs a true database delete by delegating to the parent Model.delete(). Use when
        permanent removal is required.
    - restore(self, *, commit=True):
        Clears deleted_at to mark the instance as live again. If commit=True, the instance is saved
        (updates deleted_at and updated_at); otherwise, the change remains only in memory.
    - is_deleted (property):
        Boolean convenience property that returns True if deleted_at is set.
    Usage Notes
    - Inherit this class for models that need soft-delete semantics and shared timestamp fields.
    - Prefer objects for normal queries to avoid returning soft-deleted rows; use all_objects
      when you need to access or manage deleted records.
    - The save calls use update_fields to minimize the columns updated; be mindful of any
      model signal handlers or custom save overrides that depend on full saves.
    - Consider wrapping multi-row hard deletes or restores in transactions when performing bulk operations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()             # فقط رکوردهای زنده
    all_objects = SoftDeleteQuerySet.as_manager()  # همه رکوردها

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["deleted_at", "updated_at"])]

    def delete(self, using=None, keep_parents=False):
        if self.deleted_at is None:
            self.deleted_at = timezone.now()
            self.save(update_fields=["deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self, *, commit=True):
        self.deleted_at = None
        if commit:
            self.save(update_fields=["deleted_at", "updated_at"])
        return self
    
    # برای خوانایی بهتر    
    @property
    def is_deleted(self):
        """
        Boolean convenience property that returns True if deleted_at is set.
        """
        return self.deleted_at is not None
