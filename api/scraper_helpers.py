def parse_def(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Match Report"])
    df.columns = ["Date", "Tkl", "TklW", "TklDef3rd", "TklMid3rd", "TklAtt3rd", "DriTkl", "DriChall", "Tkl%", "ChallLost", "Blocks", "ShBlk", "PassBlk", "Int", "Tkl+Int", "Clr", "Err"]
    return df

def parse_gca(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Match Report"])
    df.columns = ["Date", "SCA", "SCALivePass", "SCADeadPass", "SCADri", "SCASh", "SCAFls", "SCADefAc", "GCA", "GCALivePass", "GCADeadPass", "GCADri", "GCASh", "GCAFls", "GCADefAc"]
    return df

def parse_gk(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Match Report"])
    df.columns=["Date", "SoTA", "Saves", "Save%", "CS", "PSxG", "PSxG+/-", "PKattAg", "PKConc", "PKsvAg", "PKMissAg", "LauCmp", "LauAtt", "LauCmp%", "PassAtt", "ThrowsAtt", "PassLaunch%", 
                "PassAvgLen", "GKAtt", "GKLaunch%", "GKAvgLen", "CrossesFaced", "CrossesStp", "CrossesStp%", "DefActionOutBox", "AvgDistOfDefAction"]
    return df

def parse_misc(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "2CrdY", "Int", "TklW", "OG", "Match Report"])
    df.columns = ["Date", "Yell", "Red", "Fouls", "FoulsDrawn", "Off", "Crosses", "PKwon", "PKcon", "Recov", "AerialWon", "AerialLost", "AerialWon%"]
    return df

def parse_pass(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Match Report"])
    df.columns = ["Date", "TotPassCmp", "TotPassAtt", "TotPassCmp%", "TotPassDist", "PrgPassDist", "SPassCmp", "SPasAtt", "SPasCmp%", "MPasCmp", "MPasAtt", "MPasCmp%", 
                    "LPasCmp", "LPasAtt", "LPasCmp%", "Ast", "xAG", "xA", "KeyPasses", "PassIntoFinal1/3", "PassdIntoBox", "CrsIntoBox", "PrgPass"]
    return df

def parse_poss(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Match Report"])
    df.columns = ["Date", "Poss", "Touches", "DefBoxTouches", "Def3rdTouches", "Mid3rdTouches", "Att3rdTouches", "AttBoxTouches", 
                    "Live", "AttTakeOns", "SuccTakeOns", "Succ%TakeOns", "TkldInTakeOns", "Tkld%InTakeOns", "Carries", "TotDistCarried", 
                    "PrgDistCarried", "PrgCarries", "CarriesInto1/3", "CarriesIntoBox", "Miscontrols", "Dispossessed", "PassesRec", "PrgPassesRec"]
    return df

def parse_passTypes(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Att", "Cmp", "Match Report"])
    df.columns = ["Date", "LivePass", "DeadPass", "PassesFK", "TB", "Switch", "Cross", "TI", "CK", "CKIn", "CKOut", "CKStraight", "OffPasses", "BlockedPasses"]
    return df

def parse_shooting(df):
    df.columns = df.columns.droplevel()
    df = df.drop(columns=["Time", "Comp", "Round", "Day", "Venue", "Result", "GF", "GA", "Opponent", "Gls", "Match Report"])
    df.columns = ["Date", "Sh", "SoT", "SoT%", "G/Sh", "G/SoT", "AvgDistOfSh", "FK", "PK", "PKattFor", "xG", "npxG", "npxG/Sh", "G-xG", "np:G-xG"]
    return df