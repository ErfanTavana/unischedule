from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from institutions.models import Institution


# Triggered immediately before each ``Institution`` is saved so that the slug is always
# normalized. This avoids duplicate-looking slugs that differ only by casing or spacing
# and guarantees predictable URLs even when admins forget to supply a slug manually.
@receiver(pre_save, sender=Institution)
def ensure_institution_slug(sender, instance: Institution, **kwargs) -> None:
    if not instance.slug:
        instance.slug = slugify(instance.name)
    else:
        instance.slug = slugify(instance.slug)
