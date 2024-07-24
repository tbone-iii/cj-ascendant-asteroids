import os
import json
import random
import sys
from pathlib import Path

import openai
import feedparser
import datetime

openai.api_key = sys.argv[1]
GPT_MODEL = "gpt-4"
NEWS_API_KEY="589889c3716740ca8fc4c9c6413bac96"
NEWS_SITE_RSS_URL = "https://finance.yahoo.com/rss/"

JSON_LOCATION = Path(__file__).resolve().parent / 'articles.json'

INPUT_ARTICLE = r"""Breaking Down the Trump Family Tree
5 minute read
2024 Republican National Convention: Day 4
Donald Trump was joined by some of his children and grandchildren after his speech at the Republican National Convention in Milwaukee, Wisconsin, on July 18, 2024.Chip Somodevilla–Getty Images
By Rebecca Schneid
July 20, 2024 1:12 PM EDT

At the Republican National Convention, Donald Trump officially assumed his role as the GOP’s nominee for the 2024 presidential election and announced Ohio Senator J.D. Vance as his running mate.

It was not just the patriarch of the Trump family that took center stage at the RNC, but Trump’s sons, Donald Trump Jr. and Eric Trump, and his granddaughter, Kai Trump, who also addressed the crowd. Trump’s wife Melania and his daughter Ivanka were present at the convention, though they did not speak.

With the Trumps firmly in the limelight, here is a breakdown of the business mogul and former President’s family tree.
Donald Trump Jr.

Trump’s eldest son, and one of three children from his first marriage with the late Ivana Trump, has assumed a public-facing role throughout his father’s business and political career. He serves as executive vice president in The Trump Organization and often champions his father’s Make America Great Again campaign. At the time of publication, Trump Jr. has over 11 million followers on X (formerly Twitter). Over a decade before his father was elected president in 2016, Trump Jr. was arrested for "public intoxication" in downtown New Orleans.

In 2021, Trump Jr. launched a lifestyle media brand called Field Ethos.

He was previously married to Vanessa Trump, with whom he shares five children—Kai, 17, Donald Trump III, 15, Tristan, 12, Spencer, 11, and Chloe, 10. He is now engaged to Kimberly Guilfoyle.
Kimberly Guilfoyle 

Donald Trump Jr.’s fiancée, a former prosecutor in San Francisco and Los Angeles, also took to the stage at the RNC. Guilfoyle, 55, is the former wife of Democratic California Gov. Gavin Newsom and served as the first lady of San Francisco in the first two years Newsom served as Mayor, from 2003 to 2005.

Guilfoyle has a son, Ronan, from a previous marriage to businessman Eric Villency, who she wed after Newsom.
TOPSHOT-US-REPUBLICAN-CONVENTION-PARTIES-ELECTION-POLITICS-VOTE
Kimberly Guilfoyle speaks during the third day of the 2024 Republican National Convention at the Fiserv Forum in Milwaukee, Wisconsin, on July 17, 2024. Jim Watson—Getty Images
Kai Trump

Trump Jr.’s eldest daughter, Kai Trump, addressed the crowd at the RNC to “show a side of [her] grandpa that people don’t usually see,” making her public speaking debut. Kai, 17, is an avid golfer, and is on the varsity team at her high school in Florida.
2024 Republican National Convention
Donald Trump Jr. claps as his daughter Kai Madison Trump speaks at the Republican National Convention in Milwaukee on Wednesday, July 17, 2024. Bill Clark—Getty Images

Read More: Historians See Echoes of 1968 in Trump Assassination Attempt
Ivanka Trump

Trump’s eldest daughter, Ivanka Trump, has frequently accompanied him on the campaign trail or acted as a surrogate for her father. During her father’s presidency, Ivanka, 42, was a senior advisor in his administration, and also was the director of the Office of Economic Initiatives and Entrepreneurship. Since her father’s presidency, though, she has retreated from politics and the public eye. She did not speak at the 2024 RNC, but she did make an appearance on computer scientist Lex Fridman’s podcast, which was released in early July.
Trump Holds a Meeting with Members of his Cabinet
Jared Kushner, at the time White House Senior Advisor, and Ivanka Trump attend a meeting in the Cabinet Room of the White House in Washington, D.C. in 2018.Michael Reynolds—Getty Images
Jared Kushner

Ivanka’s husband, 43, is a business mogul in his own right. The CEO of New Jersey real estate empire Kushner Companies and publisher of the New York Observer is the son of Charles Kushner, a real estate developer who founded Kushner Companies.

The Kushner-Trump couple reported between $172m and $640m in outside income while working in the White House, according to analysis by CREW. after Trump left the White House, Kushner's private equity firm received a $2 billion investment from Saudi Arabia's sovereign wealth fund.

Ivanka and Jared share three children—Arabella, 13, Joseph, 10, and Theodore, 8.

Read More: America Met a New, Kinder Trump—Then Came the Rest of the Speech
Eric Trump

Former President Trump’s son Eric, 40, maintains less of a public persona than his older brother, but still has a leading presence in the Trump family business. Eric spoke at the RNC in defense of his father’s presidential candidacy. Eric, like his brother, is an executive vice president at The Trump Organization.
2024 Republican National Convention: Day 2
Eric Trump, son of former U.S. President Donald Trump, attends the second day of the Republican National Convention at the Fiserv Forum on July 16, 2024.Joe Raedle—Getty Images
Lara Trump

Eric’s wife, Lara Trump, is a one-time CBS producer. She took center stage at the 2024 RNC, closing the second day of the convention. She focused her speech on Trump’s role as grandparent to her children with Eric.

Lara, 41, has co-chaired the Republican National Committee since March 2024, and has been a major fundraiser for the party, helping them rake in more than $280 million since March. In the past few years, she has risen the ranks in the Republican party, and is overseeing the organization’s early voting drive, dubbed “Swamp the Vote,” a nationwide initiative to encourage Republicans to vote by mail. Eric and Lara share two children–Eric Trump Jr., 6, and Carolina, 4.
Former President Trump Addresses The North Carolina GOP Convention
Laura Trump speaks at the NCGOP state convention alongside U.S. President Donald Trump on June 5, 2021, in Greenville, North Carolina.Melissa Sue Gerrits—Getty Images

Read More: The Biden Dilemma
Tiffany Trump

Donald Trump’s fourth child, Tiffany, stood with her father in the arena at the RNC. Tiffany, 30, is Trump's only child with second wife and actress Marla Maples, to whom he was married between 1993 and 1999. In 2011, Tiffany released a pop song called “Like a Bird.” She has spoken to the public a few times during her father’s political career, and made a speech during the 2016 RNC.
2024 Republican National Convention: Day 2
Tiffany Trump walks with her husband Michael Boulos on the second day of the 2024 Republican National Convention at the Fiserv Forum.Andrew Harnik—Getty Images
Michael Boulos

Michael Boulos is a businessman, who’s family, according to Page Six, founded SCOA Nigeria and Boulos Enterprises. He married Tiffany in November 2022.

Read More: How America Can Still Come Together
Barron Trump

Donald Trump’s youngest son, Barron, now 18, largely stays out of the limelight. Throughout his childhood and his father’s presidency, Barron attended private high schools in the New York, Washington D.C., and Palm Beach areas.
Donald Trump Campaigns In Florida
Barron Trump during a campaign event at Trump National Doral Golf Club in Miami, Florida, on Tuesday, July 9, 2024. Eva Marie Uzcategui—Bloomberg

In May 2024, Barron graduated from Oxbridge Academy in Palm Beach, Florida, though he has not announced where he will attend college. Barron joined his father on the campaign trail in July at a rally in Doral, Florida."""

class Article:
    def __init__(self, body_text: str, summery: str, 
                 topic: str="General", 
                 size: str="Small", 
                 date: datetime.datetime=datetime.datetime.now(), 
                 url: str="", author: str=GPT_MODEL):

        self.body_text = body_text
        self.topic = topic
        self.size = size
        self.date = date
        self.url = url
        self.author = author

        self.summery = summery
        self.sentence_options = []

        scanning = False
        for char in list(self.summery):
            if char == '<' or char == '[':
                if char == '[': 
                    self.incorrect_option = len(self.sentence_options)

                self.sentence_options.append("")
                scanning = True

            elif char == '>' or char == ']':
                scanning = False

            elif scanning:
                self.sentence_options[-1] += char

    def __repr__(self):
        options_out = ""
        for num, sentence in enumerate(self.sentence_options):
            if num == self.incorrect_option:
                options_out += f"NOT TRUE -> {num}: {sentence}"
            else:
                options_out += f"{num}: {sentence}"

            if len(sentence) > 80:
                options_out += " TOOLONG"

            options_out += "\n"

        return f"""
----- INFO -----
Topic: {self.topic}
Size: {self.size}
Date: {self.date}
URL: {self.url}
Author: {self.author}
----- TEXT BODY START -----
{self.body_text}
----- TEXT BODY END -----

----- SUMMERY START -----
{self.summery}
----- SUMMERY END -----

----- OPTIONS START -----
{options_out}
----- OPTIONS END -----
"""

    def write(self) -> None:
        '''Adds this articles to the json file list of articles'''

        articles = Article.collect_articles()

        articles.append({
            "body_text": self.body_text,
            "summery": self.summery,
            "url": self.url,
            "topic": self.topic,
            "size": self.size,
            "date": "{}-{}-{}".format(self.date.year, self.date.month, self.date.day),
            "author": self.author
        })

        with open(JSON_LOCATION, 'w') as f:
            json.dump(articles, f)

    @staticmethod
    def collect_articles() -> dict:
        '''Collects all articles jsons from file'''

        articles = []
        with open(JSON_LOCATION) as f:
            data = json.load(f)
            for article in data:
                articles.append(article)

        return articles

    @staticmethod
    def create_article_with_json(data: json):
        '''Creates an instance of Article with the given json data'''
        return Article(data["body_text"],
                       data["summery"],
                       data["topic"],
                       data["size"],
                       datetime.datetime(data["date"]),
                       data["url"],
                       data["author"])

    @staticmethod
    def pick_random():
        '''Picks and returns a random Article type from the json saved list'''
        articles = Article.collect_articles()
        picked_article = random.choice(articles)
        return Article.create_article_with_json(picked_article)

def getGPTResponse(prompt_text:str):
    response = openai.chat.completions.create(
        model=GPT_MODEL,
        messages=[
           {"role": "system", "content": prompt_text},
           ]
    )
    
    return response.choices[0].message.content

def getSummery(article_body: str) -> str:
    # res = getGPTResponse("Please summarize the following article\n \
    # I need you to add in a fake sentence with false facts for a game, please surround this sentence with []\n \
    # Please pick 3 other sentences, don't change them, just put <> around them\n" + article_body)

    res = getGPTResponse("Please summarize the following article in around facts, each fact sentence should be no longer than 10 words, \
                         label 3 of these sentces with <> (Please don't include bullet points or numbers in the brackets) \
                         then add a sentence containing fake information, wrapped in [] instead\n \
                         Please never but [] inside of <> or vise versa\n \
    " + article_body)

    return res

# [] is fake
# <> is real
article_body_text = getGPTResponse("Generate an article based on cats that is under 300 words")
article = Article(article_body_text, getSummery(article_body_text))
article.write()
print(article)
