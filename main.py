from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def get_curr_seeding(average_win_rates, should_print=True):
    player_standing = []

    # Sort average win-rates by value
    sorted_average_win_rates = sorted(
        average_win_rates.items(), key=lambda x: x[1], reverse=True)
    
    if should_print:
        print("\n>>> Seeding:")

    # Print the sorted average win-rates player names, one per line w/ index
    for i, (player_name, avg_win_rate) in enumerate(sorted_average_win_rates):
        player_standing += [player_name]
        if should_print:
            print(i+1, player_name, avg_win_rate)

    return player_standing

# Read URLs from file
with open('players.txt', 'r') as f:
    urls = [line.strip() for line in f]

# Set up the webdriver
driver = webdriver.Chrome()

average_win_rates = {}
player_records = {}

print("\n>>> Calculating...")
# Loop over URLs
for url in urls:
    driver.get(url)

    # Wait for the page to load
    wait = WebDriverWait(driver, 60)
    elements = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, 'css-k9b79k')))

    # Get the second search field with class 'Search_textInput__2opNd'
    search_field = driver.find_elements(
        By.CLASS_NAME,  'Search_textInput__2opNd')[1]

    # Read player names from file
    with open('search.txt', 'r') as f:
        players = [line.strip() for line in f]

    # Initialize dictionary to store win rates for each player
    win_rates = {}

    # Loop over players
    for player in players:
        # Input player name into search field
        search_field.clear()
        search_field.send_keys(player)
        search_field.send_keys(Keys.RETURN)

    # Get the page source
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find the win rate data
    rows = soup.find_all('div', class_='css-k9b79k')
    for row in rows:
        player_name = row.find('div', class_='css-k6n90a')
        win_rate = row.find('div', class_='css-he2tnk')
        if player_name and win_rate and player_name.text in players:
            # Remove % sign from win rate and convert to float
            win_rate_val = float(win_rate.text.replace('%', ''))
            # Add win rate to dictionary for player
            if player_name.text in win_rates:
                win_rates[player_name.text] += win_rate_val
            else:
                win_rates[player_name.text] = win_rate_val

    player_name = soup.find('div', class_='css-1ob8mn4').text
    player_records[player_name] = win_rates

    # Sum all the win rates for each player and divide by length of win_rates
    avg_win_rate = sum(win_rates.values()) / len(win_rates)

    # Add player_name, and average win rate to a dictionary
    average_win_rates[player_name] = avg_win_rate

iteration = 0
while True:
    print("\n>>> Iteration: " + str(iteration) + " <<<")
    player_standing = get_curr_seeding(average_win_rates)

    for win_rates in player_records.values():
        for competitor in win_rates.keys():
            player_index = player_standing.index(competitor) + 1

            # Assign win value based on player index + 1
            # 1st-8th: 4 points,
            # 9th-16th: 3 points,
            # 17th-24nd: 2 points,
            # 25th-32nd: 1 point
            if player_index < 8:
                win_value = 4
            elif player_index < 16:
                win_value = 3
            elif player_index < 24:
                win_value = 2
            else:
                win_value = 1

            # Multiply win rate by win value
            win_rates[competitor] *= win_value

    # Calculate the average win rate for each player
    for player, win_rates in player_records.items():
        # Sum all the win rates for each player and divide by length of win_rates
        avg_win_rate = sum(win_rates.values()) / len(win_rates)
        # Update the average win rate for the player
        average_win_rates[player] = avg_win_rate
    
    next_player_standing = get_curr_seeding(average_win_rates, False)
    if player_standing == next_player_standing:
        break
    else:
        iteration += 1

# Close the webdriver
driver.close()