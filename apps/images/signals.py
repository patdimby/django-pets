"""Keep denormalized like counts correct from either side of the relation."""
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Image


@receiver(m2m_changed, sender=Image.users_like.through)
def users_like_changed(sender, instance, action, reverse, pk_set, **kwargs):
    if reverse and action == 'pre_clear':
        # post_clear has no primary-key set, so retain affected images beforehand.
        instance._cleared_image_ids = list(instance.images_liked.values_list('pk', flat=True))
    if action not in {'post_add', 'post_remove', 'post_clear'}:
        return
    if reverse:
        ids = pk_set if action != 'post_clear' else getattr(instance, '_cleared_image_ids', [])
        images = Image.objects.filter(pk__in=ids)
    else:
        images = [instance]
    for image in images:
        image.total_likes = image.users_like.count()
        Image.objects.filter(pk=image.pk).update(total_likes=image.total_likes)
