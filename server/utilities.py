def get_predictors_basic() -> list:
    general = ["venue_code", "team_code", "day_code", "promoted", "days_since_last_game", "is_first_game"]
    attacking = ["gf", "xg", "sh", "sot", "npxg", "npxg_per_sh"]
    defense = ["int", "xga", "ga"]
    gk = ["sota", "saves", "save_pct", "psxg"]

    extra = [
        "xg_rolling_diff",
        "xg_mean_diff",
        "xa_rolling_diff",
        "xa_mean_diff",
        "xga_rolling_diff",
        "xga_mean_diff",
        "gf_rolling_diff",
        "gf_mean_diff",
        "ga_rolling_diff",
        "ga_mean_diff",
    ]

    base = attacking + defense + gk

    home_stats = [f"{x}_atHome_rolling" for x in base] + [f"{x}_atHome_mean" for x in base]
    away_stats = [f"{x}_atAway_rolling" for x in base] + [f"{x}_atAway_mean" for x in base]

    home_stats = [f"{x}_forHomeTeam" for x in home_stats] + [f"{x}_forAwayTeam" for x in home_stats]
    away_stats = [f"{x}_forHomeTeam" for x in away_stats] + [f"{x}_forAwayTeam" for x in away_stats]

    # Stats regardless of home/away
    overall_home = [f"{x}_rolling_forHomeTeam" for x in base] + [f"{x}_mean_forHomeTeam" for x in base]
    overall_away = [f"{x}_rolling_forAwayTeam" for x in base] + [f"{x}_mean_forAwayTeam" for x in base]

    # Seasonal performance stats
    szn_perf = ["szn_cum_pts", "szn_win_pct", "szn_draw_pct", "szn_loss_pct"]
    
    szn_perf_home_away = [f"{x}_atHome" for x in szn_perf] + [f"{x}_atAway" for x in szn_perf]
    szn_perf_final = szn_perf + szn_perf_home_away
    szn_perf_final = [f"{x}_forHomeTeam" for x in szn_perf_final] + [f"{x}_forAwayTeam" for x in szn_perf_final]


    predictors = [f"{x}_forHomeTeam" for x in general] + [f"{x}_forAwayTeam" for x in general] + home_stats + away_stats + overall_home + overall_away + szn_perf_final

    # Remove all predicotrs that contain forHomeTeam and atAway or forAwayTeam and atHome
    predictors = [col for col in predictors if not (("forHomeTeam" in col and "atAway" in col) or ("forAwayTeam" in col and "atHome" in col))] + extra

    return predictors


def get_predictors() -> list:
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