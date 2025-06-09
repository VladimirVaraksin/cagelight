def injury_warning(player_actions, match_time, threshold=10):
    """
    Check for players who has not acted within a specified threshold time.

    :param player_actions: Dictionary with player IDs as keys and their last action data as values.
    :param match_time: Current match time in seconds.
    :param threshold: Time in seconds to check for inactivity.
    :return: List of player IDs who have not acted within the threshold time.
    """
    inactive_players = []

    for player_id, action in player_actions.items():
        action_desc = action[0]  # Get the last action description
        action_time = action[1]  # Get the timestamp of the last action
        time_diff = match_time - action_time

        if time_diff > threshold:
            inactive_players.append((player_id, action_desc, time_diff))
            #print(f"Warning: Player {player_id} has been {action_desc} for {time_diff:.2f} seconds.")

    return inactive_players
