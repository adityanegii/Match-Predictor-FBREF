def get_predictors_basic():
    general = ["venue_code", "team_code", "day_code", "promoted", "days_since_last_game", "is_first_game"]
    attacking = ["gf", "xg", "sh", "sot", "npxg", "npxg_per_sh"]
    defense = ["int", "xga", "ga"]
    gk = ["sota", "saves", "save_pct", "psxg"]

    base = attacking + defense + gk
    home_stats = [f"{x}_home_rolling" for x in base] + [f"{x}_home_mean" for x in base]
    away_stats = [f"{x}_away_rolling" for x in base] + [f"{x}_away_mean" for x in base]
    home_stats = [f"{x}_home" for x in home_stats] + [f"{x}_away" for x in home_stats]
    away_stats = [f"{x}_home" for x in away_stats] + [f"{x}_away" for x in away_stats]
    overall_home = [f"{x}_rolling_home" for x in base] + [f"{x}_mean_home" for x in base]
    overall_away = [f"{x}_rolling_away" for x in base] + [f"{x}_mean_away" for x in base]
    predictors = [f"{x}_home" for x in general] + [f"{x}_away" for x in general] + home_stats + away_stats + overall_home + overall_away
    return predictors



def get_predictors():
    general = ["venue_code", "team_code", "day_code", "promoted"]
    attacking = ["gf", "xg", "sh", "sot", "npxg", "npxg_per_sh"]
    # passing = ["totpasscmp", "totpassatt", "totpasscmp_pct", "totpassdist", "prgpassdist", "xag", "xa", "keypasses"]
    passing = ["xag", "xa", "keypasses"]
    gk = ["sota", "saves", "save_pct", "psxg"]
    ca = ["sca", "gca", "sca_live_pass", "gca_live_pass"]
    # possesion = ["poss", "att3rdtouches", "attboxtouches", "atttakeons", "succtakeons", "carries", "totdistcarried", "prgdistcarried"]
    defense = ["tkls", "tkls_won", "tkls_def_3rd", "tkls_mid_3rd", "tkls_att_3rd", "blocks", "int", "xga", "ga"]
    # misc = ["fouls", "foulsdrawn", "recov", "aerialwon_pct"]

    base = attacking + passing + gk + ca + defense
    overall_home = [f"{x}_rolling_home" for x in base] + [f"{x}_mean_home" for x in base]
    overall_away = [f"{x}_rolling_away" for x in base] + [f"{x}_mean_away" for x in base]

    home_stats = [f"{x}_home_rolling" for x in base] + [f"{x}_home_mean" for x in base]
    away_stats = [f"{x}_away_rolling" for x in base] + [f"{x}_away_mean" for x in base]

    home_stats = [f"{x}_home" for x in home_stats] + [f"{x}_away" for x in home_stats]
    away_stats = [f"{x}_home" for x in away_stats] + [f"{x}_away" for x in away_stats]

    predictors = [f"{x}_home" for x in general] + [f"{x}_away" for x in general] + home_stats + away_stats + overall_home + overall_away

    # with open("data/cols.txt", "r") as f:
    #     cols = [line.strip() for line in f]
    
    # base = [f"{x}_rolling" for x in cols] + [f"{x}_mean" for x in cols]
    # predictors = [f"{x}_home" for x in base] + [f"{x}_away" for x in base]  + [f"{x}_home" for x in general] + [f"{x}_away" for x in general]
    
    # return predictors
    return get_predictors_basic()

def map_predicted_result(row):
    if row['Predicted_Result'] == 0:
        return row['Away_Team']
    elif row['Predicted_Result'] == 1:
        return 'Draw'
    elif row['Predicted_Result'] == 2:
        return row['Home_Team']