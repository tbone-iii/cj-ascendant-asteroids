from random import randint

from discord import ButtonStyle, Embed, Interaction
from discord.ui import Button, View, button

from .pagination import PaginationView


class ButtonView(View):
    """Creates a view subclass containing buttons and their callback functions.

    Note: Whenever this view is created, all of the buttons get created with it.
          Perhaps theres a way to improve modularity of view/button creation, but
          for now this is what we've got. If you have any ideas, let them be known!

    """

    def __init__(self, interaction: Interaction, embed: Embed) -> None:
        super().__init__()
        self.interaction = interaction
        self.embed = embed

    # Need a function to create data/embeds for pagination (testing purposes)
    # When actually implementing, we'll fetch and use article data from the DB
    def generate_data(self, length: int) -> list[dict]:
        """Generate pagination data."""
        data = []
        for i in range(length):
            embed = Embed(
                title=f"{self.embed.title}, {self.embed.fields[1].value}",
                description=f"Page or article (idk) {i}",
                color=self.embed.color,
            )
            embed.set_thumbnail(url=self.embed.thumbnail.url)
            embed.add_field(name="Article", value="yada " * randint(3, 200))  # NOQA: S311
            data.append(
                {
                    "embed": embed,
                    "title": str(i),
                    "description": str(i) * 2,
                    "num": i + 1,
                },
            )
        return data

    @button(label="Start", style=ButtonStyle.blurple)
    async def button_callback1(
        self,
        interaction: Interaction,
        _: Button,
    ) -> None:
        """Responds to button interaction.

        Description: Callback function for the button initialized by decorator.
        """
        await self.interaction.delete_original_response()
        # Testing responses after deletion
        await interaction.response.defer()

        view = PaginationView(
            interaction.user.id,
            self.generate_data(25),
        )
        await interaction.followup.send(embed=view.data[0]["embed"], view=view)
        await view.wait()
