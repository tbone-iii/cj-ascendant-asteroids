from article_overload.bot import ArticleOverloadBot
from article_overload.constants import TOKEN

if __name__ == "__main__":
    bot = ArticleOverloadBot()
    bot.initialize(TOKEN)
