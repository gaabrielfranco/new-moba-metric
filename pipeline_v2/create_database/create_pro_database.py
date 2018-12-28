import urllib3
import json
import time


def main():
    http = urllib3.PoolManager()
    f = open("matches.txt", "r")
    matches = f.readlines()

    count_not_human = 0
    for match in matches:
        new_match = match.replace("\n", "")
        r = http.request(
            'GET', 'https://api.opendota.com/api/matches/' + new_match)

        if r.status == 200:
            print("Successful request! Match_id = ", new_match)
            data_dict = json.loads(r.data.decode("utf-8"))
            # Patch 19 é o patch 7, abaixo dele são os 6.xx
            if data_dict["patch"] < 19:
                break
            if data_dict["human_players"] == 10:
                with open("pro_database/" + new_match + ".json", "w") as outfile:
                    json.dump(data_dict, outfile)
            else:
                count_not_human += 1
        else:
            print("Request failed! Waiting 10 seconds...")
            time.sleep(10)
    print("Not human matches = %d" % count_not_human)


if __name__ == "__main__":
    main()
