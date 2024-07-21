# Python Discord Code Jam 11 - Ascendent Asteroids

## Article Overload: Anti-Cyberwarfare

### Stress Testing the Human Mind
In an era of mass information, we are constantly being inundated with disinformation and misinformation. Now, with large language models that we call AI, we're being swamped by false information, whether it is intentional or not. So what better way to learn how to deal with this than by putting yourself to the test!

In this Discord application, come to battle other players to a game of fast processing, seeing how quickly you can spot the lies in the midst of news. Be wary though, because your opponents can attack you with powerful warfare strategies like DDOS attacks, malware injections, phishing attacks, propaganda, and much more.


### Game Mechanics

 - Overload Ability: Each player has a unique cooldown ability, "CrowdStrike (Cloud Strike)," that can obfuscate the board.
 - News Flash Attack: When hit by the cooldown, players must quickly read and respond to a flashed news article.
 - Propaganda Warfare: Articles serve as attacks, containing hidden messages or links that players must decipher to counter.
 - Masked Titles: Article titles like "XX-YY-ZZZZ" hint at numbers or codes players must find.
 - Option Sets: Players counter attacks by selecting correct summary options of the article, mixing truths and falsehoods (e.g., "Earth is flat, sun isn’t real, birds are drones").
 
### Psychological Warfare
- Timer Pressure: Players have limited time (e.g., 15 seconds) to respond.
- Flashing Animations: Visual overloads to complicate reading and decision-making.
- Dynamic Options: Answer choices reorder every few seconds to increase difficulty.



### Style: Ruff

It will check your codebase and warn you about any non-conforming lines.
It is run with the command `ruff check` in the project root.

Here is a sample output:

```shell
$ ruff check
app.py:1:5: N802 Function name `helloWorld` should be lowercase
app.py:1:5: ANN201 Missing return type annotation for public function `helloWorld`
app.py:2:5: D400 First line should end with a period
app.py:2:5: D403 First word of the first line should be capitalized: `docstring` -> `Docstring`
app.py:3:15: W292 No newline at end of file
Found 5 errors.
```

Each line corresponds to an error. The first part is the file path, then the line number, and the column index.
Then comes the error code, a unique identifier of the error, and then a human-readable message.

If, for any reason, you do not wish to comply with this specific error on a specific line, you can add `# noqa: CODE` at the end of the line.
For example:

```python
def helloWorld():  # noqa: N802
    ...

```

This will ignore the function naming issue and pass linting.


### Entering the virtual environment

It will change based on your operating system and shell.

```shell
# Linux, Bash
$ source .venv/bin/activate
# Linux, Fish
$ source .venv/bin/activate.fish
# Linux, Csh
$ source .venv/bin/activate.csh
# Linux, PowerShell Core
$ .venv/bin/Activate.ps1
# Windows, cmd.exe
> .venv\Scripts\activate.bat
# Windows, PowerShell
> .venv\Scripts\Activate.ps1
```

#### Installing the dependencies

Once the environment is created and activated, use this command to install the development dependencies.

```shell
pip install -r requirements-dev.txt
```

#### Exiting the environment

```shell
deactivate
```

Once the environment is activated, all the commands listed previously should work.
