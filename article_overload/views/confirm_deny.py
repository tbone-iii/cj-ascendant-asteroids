from enum import Enum

from discord import ButtonStyle, Interaction
from discord.ui import Button, View, button


class ConfirmDenyOptions(Enum):
    """ConfirmDenyOptions Enum class.

    Description: Contains possible responses to the ConfirmDeny View
    :Return: None
    """

    YES = 0
    NO = 1
    EXPIRED = 2


class ConfirmDeny(View):
    """Confirm/Deny view class."""

    def __init__(self, org_user: int) -> None:
        """Subclass of View.

        Description: Initializes View subclass that will enable a user to respond with a confirmation or denial.
        :Return: None
        """
        super().__init__()
        self.value: bool | None = None
        self.org_user = org_user

    @button(
        label="Yes",
        emoji="<:Check:779247977721495573>",
        style=ButtonStyle.green,
    )
    async def confirm(
        self,
        _: Interaction,
        __: Button,
    ) -> None:
        """Confirm button.

        Description: Button to confirm.
        :Return: None
        """
        self.value = ConfirmDenyOptions.YES
        self.stop()

        self.clear_items()

    @button(label="No", emoji="<:Cross:779247977843523594>", style=ButtonStyle.red)
    async def deny(
        self,
        _: Interaction,
        __: Button,
    ) -> None:
        """Deny button.

        Description: Button to deny.
        :Return: None
        """
        self.value = ConfirmDenyOptions.NO
        self.stop()

        self.clear_items()

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Interaction check callback.

        Description: Callback for checking if an interaction is valid and the correct user is responding.
        :Return: Boolean
        """
        if interaction.user.id != self.org_user:
            await interaction.response.send_message(
                "You can't click this!",
                ephemeral=True,
            )
            return False

        return True

    async def on_timeout(self) -> None:
        """Timeout callback.

        Description: Callback for checking if the view has reached its timeout.
        :Return: None
        """
        self.value = ConfirmDenyOptions.EXPIRED
        self.stop()
