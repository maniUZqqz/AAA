import uuid

from django.utils.text import slugify


def unique_slug(model_cls, name: str, *, slug_field: str = "slug") -> str:
    """Build a unicode-safe slug, guaranteed unique for the given model."""
    base = slugify(name, allow_unicode=True) or uuid.uuid4().hex[:8]
    slug = base
    while model_cls.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base}-{uuid.uuid4().hex[:6]}"
    return slug
