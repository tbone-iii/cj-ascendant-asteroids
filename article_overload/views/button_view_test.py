from discord import ButtonStyle, Interaction
from discord.ui import Button, View, button


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

    @button(label="Increment Score", style=ButtonStyle.green)
    async def increment_score(self, interaction: Interaction) -> None:
        """Increment the player's score by 10."""
        game = interaction.client.games.get(interaction.user.id)
        if not game:
            return await interaction.response.send_message("Game not found!", ephemeral=True)
        player = game.get_player(interaction.user.id)
        if not player:
            return await interaction.response.send_message("Player not found!", ephemeral=True)
        player.update_score(10)
        await interaction.response.send_message(f"Score incremented! New score: {player.get_score()}")
        return None

    @button(label="Extend Timer", style=ButtonStyle.blurple)
    async def extend_timer(self, interaction: Interaction) -> None:
        """Extend the timer for the current question."""
        # Implement timer extension logic here
        await interaction.response.send_message("Timer extended by 10 seconds!")

    @button(label="End Game", style=ButtonStyle.red)
    async def end_game(self, interaction: Interaction) -> None:
        """End the game and show the duration."""
        game = interaction.client.games.get(interaction.user.id)
        if not game:
            return await interaction.response.send_message("Game not found!", ephemeral=True)
        game.end_game()
        duration = game.get_game_duration()
        interaction.client.games.pop(interaction.user.id)
        await interaction.response.send_message(f"Game ended! Duration: {duration}")
        return None
