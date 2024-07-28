from discord import ButtonStyle, Interaction, SelectOption
from discord.ui import Button, Select, View, button

from article_overload.constants import DifficultyTimer
from article_overload.db.items.article_handler import ArticleHandler
from article_overload.tools.embeds import create_error_embed


class StartButtonView(View):
    """View subclass containing a start button."""

    def __init__(self, org_user: int) -> None:
        super().__init__()
        self.org_user = org_user
        self.difficulty: float | None = None

    @button(label="Easy", style=ButtonStyle.green)
    async def easy_callback(self, interaction: Interaction, _: Button) -> None:
        """Responds to button interaction.

        Description: Callback function for the button initialized by decorator.
        """
        await self.difficulty_callback(interaction=interaction, difficulty=DifficultyTimer.EASY)

    @button(label="Medium", style=ButtonStyle.blurple)
    async def medium_callback(self, interaction: Interaction, _: Button) -> None:
        """Responds to button interaction.

        description: callback function for the button initialized by decorator.
        """
        await self.difficulty_callback(interaction=interaction, difficulty=DifficultyTimer.MEDIUM)

    @button(label="Hard", style=ButtonStyle.red)
    async def hard_callback(self, interaction: Interaction, _: Button) -> None:
        """Responds to button interaction.

        description: callback function for the button initialized by decorator.
        """
        await self.difficulty_callback(interaction=interaction, difficulty=DifficultyTimer.HARD)

    async def difficulty_callback(self, interaction: Interaction, difficulty: DifficultyTimer) -> None:
        """Responds to button interaction.

        description: callback function for the button initialized by decorator.
        """
        await interaction.response.defer()

        self.difficulty = difficulty.value

        self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Interaction check callback.

        Description: Callback for checking if an interaction is valid and the correct user is responding.
        :Return: Boolean
        """
        if interaction.user.id != self.org_user:
            await interaction.response.send_message("You can't click this!", ephemeral=True)
            return False

        return True


class SentenceSelect(Select):
    """Sentence select menu class."""

    CHAR_LIMIT = 97

    def __init__(self, sentences: list[str]) -> None:
        """Subclass of Select.

        Description: Initializes a subclass of a select menu to allow a user to select sentences.
        :Return: None
        """
        super().__init__(
            placeholder="Select a sentence",
            options=[
                SelectOption(
                    label=f"{n + 1}: {question[:self.CHAR_LIMIT]}",
                    value=str(n),
                )
                for n, question in enumerate(sentences)
            ],
        )

    async def callback(self, interaction: Interaction) -> None:
        """Select callback.

        Description: Callback to check if a sentence was selected.
        :Return: None
        """
        await interaction.response.defer()


class ContinueButtonView(View):
    """Continue button view class."""

    def __init__(self) -> None:
        """Subclass of View.

        Description: Initializes View subclass for a button that moves to next question in game.
        :Return: None
        """
        super().__init__()

    @button(label="Next Question")
    async def continue_question(self, interaction: Interaction, _: Button) -> None:
        """Button callback.

        Description: Callback to see if button was pressed.
        :Return: None
        """
        await interaction.response.defer()

        self.stop()


class GameView(View):
    """Game view class."""

    def __init__(self, org_user: int, article_handler: ArticleHandler, timeout: float) -> None:
        """Subclass of View.

        Description: Initializes View subclass to create a game view.
        :Return: None
        """
        super().__init__(timeout=timeout)
        self.org_user = org_user
        self.article_handler = article_handler

        self.sentence: str | None = None

        self.sentence_selection = SentenceSelect(article_handler.raw_text_active_sentences)
        self.add_item(self.sentence_selection)

    @button(label="Submit", style=ButtonStyle.green, row=1)
    async def submit_answer(self, interaction: Interaction, _: Button) -> None:
        """Button callback.

        Description: Callback to see if user wants to submit their answer.
        :Return: None
        """
        await interaction.response.defer()

        if len(self.sentence_selection.values) == 0:
            return await interaction.followup.send(
                embed=create_error_embed(
                    title="Select an Answer!",
                    description="Please select an answer choice using the select menu!",
                ),
                ephemeral=True,
            )

        # TODO: Rework, using the Sentences class created; fix the other issue by mapping sentences to
        # TODO: the SelectOptions (Discord API)
        self.sentence = (
            self.article_handler.active_sentences[int(self.sentence_selection.values[0])].text  # noqa: PD011
            if len(self.sentence_selection.values) > 0
            else None
        )

        self.stop()
        return None

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Interaction check callback.

        Description: Callback for checking if an interaction is valid and the correct user is responding.
        :Return: Boolean
        """
        if interaction.user.id != self.org_user:
            await interaction.response.send_message("You can't click this!", ephemeral=True)
            return False

        return True
