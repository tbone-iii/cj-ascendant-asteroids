from discord import ButtonStyle, Interaction, SelectOption
from discord.ui import Button, Select, View, button


class SelectOptions(Select):
    """Select menus class."""

    def __init__(
        self,
        option_titles: list,
        option_values: list,
    ) -> None:
        """Subclass of Select.

        Description: Initializes a subclass of a Select menu to allow for selection of values.

        Description:
        :Return: None
        """
        super().__init__(
            options=[
                SelectOption(
                    label=option_titles[i],
                    description=option_values[i],
                    value=option_values[i],
                )
                for i in range(len(option_titles))
            ],
            min_values=0,
            max_values=25,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Select callback.

        Description: Callback for checking if a value was selected.
        :Return: None
        """
        await interaction.response.defer()


class SelectOptionsView(View):
    """Select menu view class."""

    MAX_OPTIONS_PER_SELECT = 25

    def __init__(
        self,
        org_user: int,
        option_titles: list,
        option_values: list,
        value_range: tuple[int, int] = (1, 1),
    ) -> None:
        """Subclass of View.

        Description: Initializes View subclass to create a selection system.
        :Return: None
        """
        super().__init__(timeout=600)

        self.org_user = org_user
        self.clicked: list[str] = []
        self.min_val, self.max_val = value_range

        for i in range(0, len(option_titles), self.MAX_OPTIONS_PER_SELECT):
            self.add_item(
                SelectOptions(
                    option_titles[i : i + self.MAX_OPTIONS_PER_SELECT],
                    option_values[i : i + self.MAX_OPTIONS_PER_SELECT],
                ),
            )

    @button(label="Complete", style=ButtonStyle.green, row=4)
    async def submit(
        self,
        _: Interaction,
        __: Button,
    ) -> None:
        """Complete button.

        Description: Callback to check if a user has pressed submit to stop selection.
        :Return: None
        """
        self.clicked = [
            value
            for component in self.children
            if isinstance(component, SelectOptions)
            for value in component.values  # noqa: PD011
        ]

        self.stop()

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

        self.clicked = [
            value
            for component in self.children
            if isinstance(component, SelectOptions)
            for value in component.values  # noqa: PD011
        ]

        if len(self.clicked) < self.min_val:
            await interaction.response.send_message(
                f"Minimum selections is **{self.min_val}**! You have selected `{len(self.clicked)}` options",
                ephemeral=True,
            )

            return False

        if len(self.clicked) > self.max_val:
            await interaction.response.send_message(
                f"Maximum selections is **{self.max_val}**! You have selected `{len(self.clicked)}` options",
                ephemeral=True,
            )
            return False

        return True
