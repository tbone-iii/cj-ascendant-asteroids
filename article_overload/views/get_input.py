from discord import Button, ButtonStyle, Interaction, TextStyle
from discord.ui import button, Modal, TextInput, View


class Input(Modal):
    def __init__(self, title: str, message: str, view):
        super().__init__(title=title)

        self.view = view

        self.first = TextInput(label=message, style=TextStyle.short, required=True)
        self.add_item(self.first)

    async def callback(self, interaction: Interaction):
        self.view.response = self.first.value
        self.stop()


class Input_Button(View):
    def __init__(self, title: str, message: str, org_user: int):
        super().__init__(timeout=180)
        self.title = title
        self.message = message
        self.org_user = org_user
        self.response = None

    @button(label="Submit", style=ButtonStyle.green)
    async def submit(self, button: Button, interaction: Interaction):
        modal = Input(self.title, self.message, self)
        await interaction.response.send_modal(modal)
        await modal.wait()

        self.stop()

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False

        return True
