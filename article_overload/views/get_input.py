from discord import Button, ButtonStyle, Interaction, TextStyle
from discord.ui import Modal, TextInput, View, button


class Input(Modal):
    """Submit input modal class."""

    def __init__(self, title: str, message: str, view: View) -> None:
        """Subclass of View.

        Description: Initializes a Modal subclass that allows a user to input a value into a form.
        :Return: None
        """
        super().__init__(title=title)

        self.view = view

        self.first = TextInput(label=message, style=TextStyle.short, required=True)
        self.add_item(self.first)

    async def callback(self, interaction: Interaction) -> None:  # noqa: ARG002
        """Submit callback.

        Description: Callback to check if a user has submittted the form.
        :Return: None
        """
        self.view.response = self.first.value
        self.stop()


class InputButton(View):
    """Submit input view class."""

    def __init__(self, title: str, message: str, org_user: int) -> None:
        """Subclass of View.

        Description: Initializes View subclass that will enable a user to input a value to a question.
        :Return: None
        """
        super().__init__(timeout=180)
        self.title = title
        self.message = message
        self.org_user = org_user
        self.response = None

    @button(label="Submit", style=ButtonStyle.green)
    async def submit(
        self,
        button: Button,
        interaction: Interaction,
    ) -> None:
        """Submit button.

        Description: Callback to check if a user has pressed submit to display modal.
        :Return: None
        """
        modal = Input(self.title, self.message, self)
        await interaction.response.send_modal(modal)
        await modal.wait()

        self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Interaction check callback.

        Description: Callback for checking if an interaction is valid and the correct user is responding.
        :Return: Boolean
        """
        if interaction.user.id != self.org_user:
            await interaction.send("You can't click this!", ephemeral=True)
            return False

        return True
