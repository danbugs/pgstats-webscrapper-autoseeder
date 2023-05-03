# pgstats-webscrapper-autoseeder

This is a very scuffed autoseeder for events. For it to work, you need to provide it two text files:
1. players.txt - This file contains the list of players (i.e., the URL to their PGStats profile) that you want to seed. Each player should be on a new line.
    - e.g., https://www.pgstats.com/ultimate/player/Dantotto?id=S1178271
2. search.txt - This file contains the list of players you want to each player's win-rates against. Each player should be on a new line.
    - e.g., Dantotto

After getting the win-rates against every player in `search.txt` for each profile in `players.txt`, the program will utilize those to seed the event. The seeding is done through several iterations w/ assigning weights based on that round's stadings/seeding, and it runs until the seeding is stable (i.e., close enough to the previous iteration based on a treshold).

The output will be displayed in `stdout`.