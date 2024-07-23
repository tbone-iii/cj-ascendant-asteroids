from .utils import create_success_embed, create_warning_embed, create_error_embed


def missing_permissions(error: Exception = None):
    return create_error_embed(
        title="Missing Permissions!",
        description=f"You cannot run this command as you are missing the following permissions: {',' .join(error.missing_permissions) if error else 'Tourney'}",
    )


def action_canceled():
    return create_warning_embed(title="Action canceled")


def error_occurred():
    return create_error_embed(
        title="Error!",
        description="An error has occurred while running your command!",
    )
