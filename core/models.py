from django.db import models
from django.utils import timezone


class BaseQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        return self.filter(deleted_at__isnull=False)


class BaseManager(models.Manager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db).active()

    def all_objects(self):
        return BaseQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset()

    def deleted(self):
        return self.all_objects().deleted()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = BaseManager()

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def delete(self, hard_delete=False, **kwargs):
        if hard_delete:
            django_delete_kwargs = {k: v for k, v in kwargs.items() if k in ['using']}
            return super().delete(**django_delete_kwargs)
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, **kwargs):
        django_delete_kwargs = {k: v for k, v in kwargs.items() if k in ['using']}
        return self.delete(hard_delete=True, **django_delete_kwargs)

    def restore(self):
        self.deleted_at = None
        self.save()

    @property
    def is_active(self):
        return not self.is_deleted

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"