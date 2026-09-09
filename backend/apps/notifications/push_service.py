import json
import logging
from django.conf import settings
from .models import PushSubscription

logger = logging.getLogger(__name__)

try:
    from pywebpush import webpush, WebPushException
except ImportError:
    webpush = None
    WebPushException = Exception
    logger.warning("[AUL Push] pywebpush is not installed. Web push notifications will be skipped.")


def send_push_notification(announcement):
    """
    Отправляет Web Push уведомление всем активным подписчикам (PushSubscription)
    при создании или публикации активного оповещения аула.

    - Недействительные подписки (HTTP 404 / 410) автоматически удаляются из БД.
    - Ошибки отправки логируются и не прерывают процесс для остальных подписчиков.
    """
    if webpush is None:
        logger.error("[AUL Push] Cannot send push: pywebpush library is missing.")
        return {"total": 0, "success": 0, "failed": 0, "deleted": 0}

    vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
    vapid_email = getattr(settings, 'VAPID_CLAIMS_EMAIL', None)

    if not vapid_private_key:
        logger.error("[AUL Push] VAPID_PRIVATE_KEY is not configured in settings.")
        return {"total": 0, "success": 0, "failed": 0, "deleted": 0}

    # Подготовка VAPID claims
    if not vapid_email:
        vapid_email = "mailto:admin@aul.kz"
    elif not (vapid_email.startswith("mailto:") or vapid_email.startswith("https://")):
        vapid_email = f"mailto:{vapid_email}"

    vapid_claims = {"sub": vapid_email}

    # Формирование информативного заголовка и текста
    category_display = announcement.get_category_display()
    if announcement.is_urgent:
        title = f"🚨 {category_display}: {announcement.title}"
    else:
        title = f"📢 {category_display}: {announcement.title}"

    body = announcement.description or ""
    if len(body) > 200:
        body = body[:197] + "..."

    payload_data = {
        "title": title,
        "body": body,
        "url": "/notifications/",
        "type": announcement.announcement_type,
        "category": announcement.category,
        "icon": "/static/images/icon-192.png",
        "badge": "/static/images/icon-192.png",
        "announcement_id": announcement.pk,
    }
    payload_json = json.dumps(payload_data, ensure_ascii=False)

    subscriptions = PushSubscription.objects.all()
    total = subscriptions.count()

    if total == 0:
        logger.info("[AUL Push] No active push subscriptions in database.")
        return {"total": 0, "success": 0, "failed": 0, "deleted": 0}

    logger.info(
        f"[AUL Push] Sending announcement #{announcement.pk} to {total} subscriber(s)..."
    )

    success_count = 0
    failed_count = 0
    deleted_count = 0

    clean_private_key = vapid_private_key.strip()

    for sub in subscriptions:
        sub_info = {
            "endpoint": sub.endpoint,
            "keys": {
                "p256dh": sub.p256dh,
                "auth": sub.auth,
            },
        }

        try:
            webpush(
                subscription_info=sub_info,
                data=payload_json,
                vapid_private_key=clean_private_key,
                vapid_claims=vapid_claims,
                timeout=5,
            )
            success_count += 1
        except WebPushException as ex:
            failed_count += 1
            status_code = None
            if hasattr(ex, 'response') and ex.response is not None:
                status_code = getattr(ex.response, 'status_code', None)

            # Удаление устаревших или аннулированных подписок
            if status_code in (404, 410):
                logger.warning(
                    f"[AUL Push] Subscription #{sub.pk} is gone (HTTP {status_code}). Removing from DB."
                )
                try:
                    sub.delete()
                    deleted_count += 1
                except Exception as del_err:
                    logger.error(f"[AUL Push] Failed to delete expired subscription #{sub.pk}: {del_err}")
            else:
                logger.error(
                    f"[AUL Push] WebPushException for subscription #{sub.pk}: {ex} (status: {status_code})"
                )
        except Exception as ex:
            failed_count += 1
            logger.error(f"[AUL Push] Error sending to subscription #{sub.pk}: {ex}")

    logger.info(
        f"[AUL Push] Dispatch completed for #{announcement.pk}: "
        f"{success_count} sent, {failed_count} failed, {deleted_count} deleted."
    )

    return {
        "total": total,
        "success": success_count,
        "failed": failed_count,
        "deleted": deleted_count,
    }
