from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import copy
import sys

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

def is_seeding_stable(curr_players, prev_players, threshold):
    curr_dict = {curr_players[i]: i+1 for i in range(len(curr_players))}
    prev_dict = {prev_players[i]: i+1 for i in range(len(prev_players))}
    curr_seedings = [curr_dict[player] for player in curr_players]
    prev_seedings = [prev_dict[player] for player in curr_players]
    differences = [abs(curr_seedings[i] - prev_seedings[i]) for i in range(len(curr_seedings))]
    mad = sum(differences) / len(differences)
    return mad < threshold

# Get command-line arg to decide whether to web-scrape
if len(sys.argv) > 1 and sys.argv[1] == 'scrape':
    scrape = True
else:
    scrape = False

if scrape:
    # Read URLs from file
    with open('players.txt', 'r') as f:
        urls = [line.strip() for line in f]

    # Set up the webdriver
    driver = webdriver.Chrome()

    average_win_rates = {}
    player_records = {}
    overall_win_rates = {}

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

        # Click button with ID rcc-confirm-button, if it exists
        try:
            confirm_button = driver.find_element(By.ID, 'rcc-confirm-button')
            confirm_button.click()
        except:
            pass
        
        # Loop over players
        for player in players:
            # Input player name into search field
            search_field.clear()
            search_field.send_keys(player)
            search_field.send_keys(Keys.RETURN)

        # Find last `select` in the page, and select the third option
        select = driver.find_elements(By.TAG_NAME, 'select')[-1]
        select.click()
        options = select.find_elements(By.TAG_NAME, 'option')
        options[2].click()

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

        overall_win_rates[player_name] = float(soup.find('div', class_='css-he2tnk').text.replace('%', ''))

        # Sum all the win rates for each player and divide by length of win_rates
        avg_win_rate = sum(win_rates.values()) / len(win_rates)

        # Add player_name, and average win rate to a dictionary
        average_win_rates[player_name] = avg_win_rate

    # write player records, average_win_rates, and overall_win_rates to file
    with open('player_records.txt', 'w') as f:
        f.write(str(player_records))
    with open('average_win_rates.txt', 'w') as f:
        f.write(str(average_win_rates))
    with open('overall_win_rates.txt', 'w') as f:
        f.write(str(overall_win_rates))
else:
    # read player records, average_win_rates, and overall_win_rates from file
    with open('player_records.txt', 'r') as f:
        player_records = eval(f.read())
    with open('average_win_rates.txt', 'r') as f:
        average_win_rates = eval(f.read())
    with open('overall_win_rates.txt', 'r') as f:
        overall_win_rates = eval(f.read())

iteration = 0
initial_player_record = copy.deepcopy(player_records)
while True:
    player_records = copy.deepcopy(initial_player_record)

    print("\n>>> Iteration: " + str(iteration) + " <<<")
    if iteration == 0:
        player_standing = get_curr_seeding(overall_win_rates)
    else:
        player_standing = get_curr_seeding(average_win_rates)

    sum_of_weights = {}

    for (curr_player, win_rates) in player_records.items():

        for competitor in win_rates.keys():
            player_index = player_standing.index(competitor) + 1

            # Assign win value based on player index + 1
            if player_index < 4:
                win_value = 13
            elif player_index < 8:
                win_value = 11
            elif player_index < 12:
                win_value = 7
            elif player_index < 16:
                win_value = 4
            elif player_index < 24:
                win_value = 2
            else:
                win_value = 1

            # Multiply win rate by win value
            win_rates[competitor] *= win_value
            
            # Add win_value to sum_of_weights
            if curr_player in sum_of_weights:
                sum_of_weights[curr_player] += win_value
            else:
                sum_of_weights[curr_player] = win_value

    # Calculate the average win rate for each player
    for player, win_rates in player_records.items():
        # Sum all the win rates for each player and divide by sum of weights (i.e., weighed average)
        avg_win_rate = (sum(win_rates.values()) + len(win_rates)) / ( sum_of_weights[player])
        # Update the average win rate for the player
        average_win_rates[player] = avg_win_rate
    
    next_player_standing = get_curr_seeding(average_win_rates, False)
    if is_seeding_stable(player_standing, next_player_standing, 1):
        break
    else:
        iteration += 1

if scrape:
    # Close the webdriver
    driver.close()