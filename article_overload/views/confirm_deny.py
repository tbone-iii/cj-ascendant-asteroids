from discord import Button, ButtonStyle, Interaction
from discord.ui import button, View


class ConfirmDeny(View):
    def __init__(self, org_user: int):
        super().__init__()
        self.value = None
        self.org_user = org_user

    @button(
        label="Yes",
        emoji="<:Check:779247977721495573>",
        style=ButtonStyle.green,
    )
    async def confirm(self, button: Button, interaction: Interaction):
        self.value = True
        self.stop()

        self.clear_items()

    @button(label="No", emoji="<:Cross:779247977843523594>", style=ButtonStyle.red)
    async def deny(self, button: Button, interaction: Interaction):
        self.value = False
        self.stop()

        self.clear_items()

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False

        return True

    async def on_timeout(self):
        self.stop()
