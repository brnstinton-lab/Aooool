import json
import logging
from django.conf import settings
from .models import PushSubscription, Announcement

logger = logging.getLogger(__name__)


def get_eligible_push_subscriptions(announcement):
    """
    Возвращает QuerySet подписок пользователей, которым разрешено
    получать Push-уведомление данного типа (URGENT или OFFICIAL).

    Правила:
    1. announcement_type == URGENT:
       - Пользователи с urgent_enabled == True
       - Пользователи без записи NotificationPreference (по умолчанию True)
       - Анонимные подписки (user is None)
       - Исключаются пользователи с urgent_enabled == False
    2. announcement_type == OFFICIAL:
       - Пользователи с official_enabled == True
       - Пользователи без записи NotificationPreference (по умолчанию True)
       - Анонимные подписки (user is None)
       - Исключаются пользователи с official_enabled == False
    """
    announcement_type = announcement.announcement_type

    if announcement_type == Announcement.AnnouncementType.URGENT:
        return PushSubscription.objects.exclude(
            user__notification_preference__urgent_enabled=False
        )
    elif announcement_type == Announcement.AnnouncementType.OFFICIAL:
        return PushSubscription.objects.exclude(
            user__notification_preference__official_enabled=False
        )
    return PushSubscription.objects.none()


def send_push_notification(announcement):
    """
    Отправляет Web Push уведомления подписчикам в соответствии с их предпочтениями.
    """
    if announcement.status != Announcement.Status.ACTIVE:
        return 0

    subscriptions = get_eligible_push_subscriptions(announcement)
    count = subscriptions.count()
    if count == 0:
        return 0

    vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
    vapid_claims_email = getattr(settings, 'VAPID_CLAIMS_EMAIL', 'mailto:admin@aul.kz')

    # Формируем payload для Service Worker (sw.js)
    type_prefix = "🚨 " if announcement.is_urgent else "📢 "
    title = f"{type_prefix}{announcement.title}"
    body = announcement.description[:120] + ("..." if len(announcement.description) > 120 else "")

    payload = json.dumps({
        "title": title,
        "body": body,
        "icon": "/static/images/icon-192.png",
        "badge": "/static/images/icon-192.png",
        "url": "/notifications/",
    })

    if not vapid_private_key:
        logger.info(f"[AUL Push] Mock/Testing send to {count} subscriptions: {title}")
        return count

    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        logger.warning("[AUL Push] pywebpush is not installed")
        return count

    sent_count = 0
    vapid_claims = {"sub": vapid_claims_email}

    for sub in subscriptions:
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": {
                "p256dh": sub.p256dh,
                "auth": sub.auth,
            }
        }
        try:
            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims
            )
            sent_count += 1
        except WebPushException as ex:
            logger.warning(f"[AUL Push] WebPushException for sub {sub.id}: {ex}")
            if ex.response is not None and ex.response.status_code in (404, 410):
                sub.delete()
        except Exception as e:
            logger.warning(f"[AUL Push] Error sending push to sub {sub.id}: {e}")

    return sent_count
