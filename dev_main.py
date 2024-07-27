from article_overload.bot import ArticleOverloadBot
from article_overload.constants import TOKEN
from article_overload.log import our_logger

if __name__ == "__main__":
    bot = ArticleOverloadBot(logger=our_logger)
    bot.start_bot(TOKEN)
