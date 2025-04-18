import pandas as pd
def find_recent(server: str, channel: str, userID: str = None):
    log = pd.read_csv('log.csv').astype(str)
    find = 1
    if userID == None:
        while find < log.shape[0]:
            if log.iloc[-find]['Server'] == server and log.iloc[-find]['Channel'] == channel:
                return log.iloc[-find]['Message']
            find += 1
    else:
        while find < log.shape[0]:
            if log.iloc[-find]['UserID'] == str(userID):
                return log.iloc[-find]['Message']
            find += 1
   
    return 'หนูหาข้อความไม่เจออ่ะคะ'

def find_recent_attachment(server: str, channel: str, userID: str = None):
    log = pd.read_csv('log.csv').astype(str)
    find = 1
    if userID == None:
        while find < log.shape[0]:
            if log.iloc[-find]['Server'] == server and log.iloc[-find]['Channel'] == channel:
                if 'attachment = ' in log.iloc[-find]['Message']:
                    return log.iloc[-find]['Message']
            find += 1
    else:
        while find < log.shape[0]:
            if log.iloc[-find]['UserID'] == str(userID):
                if 'attachment = ' in log.iloc[-find]['Message']:
                    return log.iloc[-find]['Message']
            find += 1
   
    return False

# print(find_recent('Lunaar', 'bot-test'))