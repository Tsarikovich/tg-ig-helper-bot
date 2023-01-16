import json

with open("../logins.txt", "r", encoding="utf-8") as input:
    data = input.read().split()
    dict_logins = dict()

    for i, account in enumerate(data):
        login, password = account.split(',')
        curr_cred = {"login": login, "password": password}
        dict_logins[f"account{i}"] = curr_cred

    with open("../credentials.json", "w", encoding="utf-8") as output:
        json.dump(dict_logins, output, ensure_ascii=False)
