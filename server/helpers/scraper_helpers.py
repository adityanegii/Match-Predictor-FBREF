def parse_def(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Match Report"])
    df.columns = ["Date", "Tkls", "Tkls_Won", "Tkls_Def_3rd", "Tkls_Mid_3rd", "Tkls_Att_3rd", "Dri_Tkl", "Dri_Chall", "Tkl_pct", "Chall_Lost", "Blocks", "Sh_Blk", "Pass_Blk", "Int", "Tkl_plus_Int", "Clr", "Err"]
    return df

def parse_gca(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Match Report"])
    df.columns = ["Date", "SCA", "SCA_Live_Pass", "SCA_Dead_Pass", "SCA_Dri", "SCA_Sh", "SCA_Fls", "SCA_Def_Ac", "GCA", "GCA_Live_Pass", "GCA_Dead_Pass", "GCA_Dri", "GCA_Sh", "GCA_Fls", "GCA_Def_Ac"]
    return df

def parse_gk(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Match Report"])
    df.columns=["Date", "SoTA", "Saves", "Save_pct", "CS", "PSxG", "PSxG_diff", "PK_att_Ag", "PK_Conc", "PK_sv_Ag", "PK_Miss_Ag", "Lau_Cmp", "Lau_Att", "Lau_Cmp_pct", "Pass_Att", "Throws_Att", "Pass_Launch_pct", 
                "Pass_Avg_Len", "GK_Att", "GK_Launch_pct", "GK_Avg_Len", "Crosses_Faced", "Crosses_Stp", "Crosses_Stp_pct", "Def_ActionOut_Box_gk", "Avg_Dist_Of_Def_Action_gk"]
    return df

def parse_misc(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "2CrdY", "Int", "TklW", "OG", "Match Report"])
    df.columns = ["Date", "Yell", "Red", "Fouls", "Fouls_Drawn", "Off", "Crosses", "PK_won", "PK_con", "Recov", "Aerial_Won", "Aerial_Lost", "Aerial_Won_pct"]
    return df

def parse_pass(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Match Report"])
    df.columns = ["Date", "Tot_Pass_Cmp", "Tot_Pass_Att", "Tot_Pass_Cmp_pct", "Tot_Pass_Dist", "Prg_Pass_Dist", "SPass_Cmp", "SPas_Att", "SPas_Cmp_pct", "MPas_Cmp", "MPas_Att", "MPas_Cmp_pct", 
                    "LPas_Cmp", "LPas_Att", "LPas_Cmp_pct", "Ast", "xAG", "xA", "KeyPasses", "Pass_Into_Final_3rd", "Pass_Into_Box", "Crs_Into_Box", "Prg_Pass"]
    return df

def parse_poss(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Match Report"])
    df.columns = ["Date", "Poss", "Touches", "Def_Box_Touches", "Def_3rd_Touches", "Mid_3rd_Touches", "Att_3rd_Touches", "Att_Box_Touches", 
                    "Live_Touches", "Att_TakeOns", "Succ_TakeOns", "Succ_pct_TakeOns", "Tkld_TakeOns", "Tkld_pct_TakeOns", "Carries", "Tot_Dist_Carried", 
                    "Prg_Dist_Carried", "Prg_Carries", "Carries_Into_3rd", "Carries_Into_Box", "Miscontrols", "Dispossessed", "Passes_Rec", "Prg_Passes_Rec"]
    return df

def parse_passTypes(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Att", "Cmp", "Match Report"])
    df.columns = ["Date", "Live_Pass", "Dead_Pass", "Passes_FK", "Through", "Switch", "Cross", "Throw_ins", "CK", "CK_In", "CK_Out", "CK_Straight", "Off_Passes", "Blocked_Passes"]
    return df

def parse_shooting(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Gls", "Match Report"])
    df.columns = ["Date", "Sh", "SoT", "SoT_pct", "G_per_Sh", "G_per_SoT", "Avg_Dis_Of_Sh", "FK", "PK", "PK_att_For", "xG", "npxG", "npxG_per_Sh", "G_minus_xG", "npG_minus_xG"]
    return df