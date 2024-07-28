from discord import ButtonStyle, Interaction, SelectOption
from discord.ui import Button, Select, View, button

from article_overload.constants import DIGIT_TO_EMOJI, DifficultyTimer
from article_overload.db.items.article_handler import ArticleHandler
from article_overload.db.items.sentence import Sentence
from article_overload.tools.embeds import create_error_embed


class StartButtonView(View):
    """View subclass containing a start button."""

    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.start_timer_seconds: float | None = None

    @button(label="Easy", style=ButtonStyle.green)
    async def easy_callback(self, interaction: Interaction, _: Button) -> None:
        """Responds to button interaction.

        Description: Callback function for the button initialized by decorator.
        """
        await self.difficulty_callback(interaction=interaction, difficulty_timer=DifficultyTimer.EASY)

    @button(label="Medium", style=ButtonStyle.blurple)
    async def medium_callback(self, interaction: Interaction, _: Button) -> None:
        """Responds to button interaction.

        description: callback function for the button initialized by decorator.
        """
        await self.difficulty_callback(interaction=interaction, difficulty_timer=DifficultyTimer.MEDIUM)

    @button(label="Hard", style=ButtonStyle.red)
    async def hard_callback(self, interaction: Interaction, _: Button) -> None:
        """Responds to button interaction.

        description: callback function for the button initialized by decorator.
        """
        await self.difficulty_callback(interaction=interaction, difficulty_timer=DifficultyTimer.HARD)

    async def difficulty_callback(self, interaction: Interaction, difficulty_timer: DifficultyTimer) -> None:
        """Responds to button interaction.

        description: callback function for the button initialized by decorator.
        """
        await interaction.response.defer()
        self.start_timer_seconds = difficulty_timer.value
        self.stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Interaction check callback.

        Description: Callback for checking if an interaction is valid and the correct user is responding.
        :Return: Boolean
        """
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't click this!", ephemeral=True)
            return False
        return True


class SentencePicker(Select):
    """Sentence select menu class."""

    def __init__(self, sentences: list[Sentence]) -> None:
        """Subclass of Select.

        Description: Initializes a subclass of a select menu to allow a user to select sentences.
        :Return: None
        """
        options = [
            SelectOption(
                label=sentence.get_truncated_text(prefix=f"{DIGIT_TO_EMOJI.get(i, i)} "),
                value=str(i),
            )
            for i, sentence in enumerate(sentences, start=1)
        ]
        self.value_to_sentence = {str(i): sentence for i, sentence in enumerate(sentences, start=1)}

        super().__init__(
            placeholder="Select a sentence",
            options=options,
        )

    @property
    def selected_value(self) -> str:
        """Selected item."""
        return self.values[0] if self.values else ""

    @property
    def selected_sentence(self) -> Sentence | None:
        """Selected sentence."""
        return self.value_to_sentence.get(self.selected_value, None)

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

        self.sentence: Sentence | None = None  # TODO: None? Rethink

        self.sentence_picker = SentencePicker(article_handler.active_sentences)
        self.add_item(self.sentence_picker)

    @button(label="Submit", style=ButtonStyle.green, row=1)
    async def submit_answer(self, interaction: Interaction, _: Button) -> None:
        """Button callback.

        Description: Callback to see if user wants to submit their answer.
        :Return: None
        """
        await interaction.response.defer()

        if len(self.sentence_picker.values) == 0:
            return await interaction.followup.send(
                embed=create_error_embed(
                    title="Select an Answer!",
                    description="Please select an answer choice using the select menu!",
                ),
                ephemeral=True,
            )

        self.sentence = self.sentence_picker.selected_sentence
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
