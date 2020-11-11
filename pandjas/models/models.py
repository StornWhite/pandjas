from django.db import models


class ValidatingModel(models.Model):
    """
    A django model that self-validates by calling full_clean() during save.
    This in turn validates all model fields.  Subclasses of this model can
    implement object-wide validation (across multiple fields, etc) by
    implementing the clean() method.
    """
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
