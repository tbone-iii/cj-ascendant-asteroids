from discord import ButtonStyle, Interaction, SelectOption
from discord.ui import Button, Select, View, button


class PaginationSelect(Select):
    """Pagination select menu class."""

    def __init__(self, data: list, full_data: list, page: int = 0) -> None:
        """Subclass of Select.

        Description: Initializes a subclass of a Select menu to allow for easy pagination.
        :Return: None
        """
        super().__init__(
            options=[
                SelectOption(
                    label=datum["title"],
                    description=datum["description"],
                    value=datum["num"],
                )
                for datum in data
            ],
        )

        self.full_data = full_data
        self.page = page

    async def callback(self, interaction: Interaction) -> None:
        """Select callback.

        Description: Callback for checking if a value was selected.
        :Return: None
        """
        await interaction.response.edit_message(
            embed=self.full_data[int(self.values[0]) - 1]["embed"],
            view=PaginationView(
                interaction.user.id,
                self.full_data,
                page=int(self.values[0]) - 1,
            ),
        )


class PaginationView(View):
    """Pagination view class."""

    PAGE_SIZE = 25

    def __init__(self, org_user: int, data: list, page: int = 0) -> None:
        """Subclass of View.

        Description: Initializes View subclass to create a pagination system.
        :Return: None
        """
        super().__init__(timeout=600)

        self.org_user = org_user
        self.data = data
        self.page = page

        for i in range(0, len(data), self.PAGE_SIZE):
            self.add_item(
                PaginationSelect(data[i : i + self.PAGE_SIZE], self.data, page),
            )

    @button(emoji="<:left_arrow:1049429857488093275>", style=ButtonStyle.blurple)
    async def left_arrow(
        self,
        interaction: Interaction,
        _: Button,
    ) -> None:
        """Left button.

        Description: Moves page selection to the left.
        :Return: None
        """
        self.page -= 1 if self.page > 0 else 0
        await self.update_page(interaction)

    @button(emoji="<:right_arrow:1049430086257999882>", style=ButtonStyle.blurple)
    async def right_arrow(
        self,
        interaction: Interaction,
        _: Button,
    ) -> None:
        """Right button.

        Description: Moves page selection to the right.
        :Return: None
        """
        self.page += 1 if self.page < len(self.data) - 1 else 0
        await self.update_page(interaction)

    async def update_page(self, interaction: Interaction) -> None:
        """Update page.

        Description: Callback to update embed and page content.
        :Return: None
        """
        await interaction.response.edit_message(embed=self.data[self.page]["embed"])

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
