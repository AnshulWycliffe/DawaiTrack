from datetime import datetime
from flask_login import current_user

from app.models.audit_log import AuditLog


def log_action(action, entity=None, entity_id=None, description=None):

    try:

        user = current_user if current_user.is_authenticated else None

        AuditLog(
            user=user,
            action=action,
            entity=entity,
            entity_id=str(entity_id) if entity_id else None,
            description=description,
            created_at=datetime.utcnow()
        ).save()
        print("WORKING")

    except Exception:
        # logging should never break the main flow
        pass