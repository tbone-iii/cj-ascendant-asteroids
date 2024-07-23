from discord import Button, ButtonStyle, Interaction
from discord.ui import View, button


class ButtonView(View):
    """Creates a view subclass containing buttons and their callback functions.

    Note: Whenever this view is created, all of the buttons get created with it.
          Perhaps theres a way to improve modularity of view/button creation, but
          for now this is what we've got. If you have any ideas, let them be known!

    """

    @button(label="Button1", style=ButtonStyle.blurple)
    async def button_callback1(
        self,
        interaction: Interaction,
        button: Button,
    ) -> None:
        """Responds to button interaction.

        Description: Callback function for the button initialized by decorator.
        """
        button.disabled = True
        await interaction.response.edit_message(content="Button1 pressed!", view=self)

    @button(label="Button2", style=ButtonStyle.blurple)
    async def button_callback2(
        self,
        interaction: Interaction,
        button: Button,
    ) -> None:
        """Responds to button interaction.

        Description: Callback function for the button initialized by decorator.
        """
        button.disabled = True
        await interaction.response.edit_message(content="Button2 pressed!", view=self)

    @button(label="Button3", style=ButtonStyle.blurple)
    async def button_callback3(
        self,
        interaction: Interaction,
        button: Button,
    ) -> None:
        """Responds to button interaction.

        Description: Callback function for the button initialized by decorator.
        """
        button.disabled = True
        await interaction.response.edit_message(content="Button3 pressed!", view=self)

    @button(label="Button4", style=ButtonStyle.blurple)
    async def button_callback4(
        self,
        interaction: Interaction,
        button: Button,
    ) -> None:
        """Responds to button interaction.

        Description: Callback function for the button initialized by decorator.
        """
        button.disabled = True
        await interaction.response.edit_message(content="Button4 pressed!", view=self)
