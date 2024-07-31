from collections.abc import Iterable

from discord import ButtonStyle, Embed, Interaction, SelectOption
from discord.ui import Button, Select, View, button

from article_overload.exceptions import PaginationViewMissingButtonsError
from article_overload.log import our_logger


class PaginationSelect(Select):
    """Pagination select menu class."""

    def __init__(self, data: Iterable, full_data: list, page: int = 0) -> None:
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
        clicked_index = int(self.values[0])
        view = PaginationView(
            interaction.user.id,
            self.full_data,
            page=clicked_index,
        )
        embed = self.full_data[clicked_index]["embed"]
        if isinstance(self.full_data[clicked_index]["embed"], Embed):
            await interaction.response.edit_message(
                embed=embed,
                view=view,
            )
        else:
            await interaction.response.edit_message(
                embeds=embed,
                view=view,
            )


class PaginationView(View):
    """Pagination view class."""

    PAGE_SIZE = 5

    def __init__(self, org_user: int, data: list, page: int = 0) -> None:
        """Subclass of View.

        Description: Initializes View subclass to create a pagination system.
        :Return: None
        """
        super().__init__(timeout=600)

        self.org_user = org_user
        self.data = data
        self.page = page

        left_button, right_button = self.children[0], self.children[1]
        if not isinstance(left_button, Button) or not isinstance(right_button, Button):
            raise PaginationViewMissingButtonsError

        self.left_button: Button = left_button
        self.right_button: Button = right_button

        self.add_item(PaginationSelect(data=data, full_data=self.data, page=page))

    @button(emoji="<:left_arrow:1049429857488093275>", style=ButtonStyle.blurple)
    async def left_arrow(self, interaction: Interaction, _: Button) -> None:
        """Left button.

        Description: Moves page selection to the left.
        :Return: None
        """
        self.page -= 1 if self.page > 0 else 0
        await self.update_page(interaction)

    @button(emoji="<:right_arrow:1049430086257999882>", style=ButtonStyle.blurple)
    async def right_arrow(self, interaction: Interaction, _: Button) -> None:
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
        is_first_page = self.page < 1
        is_last_page = self.page == len(self.data) - 1

        self.left_button.disabled = is_first_page
        self.right_button.disabled = is_last_page

        embed_data = self.data[self.page]["embed"]
        if isinstance(self.data[self.page]["embed"], Embed):
            our_logger.debug(f"Updating page to {self.page=} for single embed")
            await interaction.response.edit_message(
                embed=embed_data,
                view=self,
            )

        else:
            our_logger.debug(f"Updating page to {self.page=} for multi-embed")
            await interaction.response.edit_message(
                embeds=embed_data,
                view=self,
            )

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Interaction check callback.

        Description: Callback for checking if an interaction is valid and the correct user is responding.
        :Return: Boolean
        """
        if interaction.user.id != self.org_user:
            await interaction.response.send_message("You can't click this!", ephemeral=True)
            return False
        return True
