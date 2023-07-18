def validate():
    f = open("coordinator-logs.txt", "r")
    lines = f.readlines()
    requests = []
    grants = []
    releases = []

    for line in lines:
        if ("[R] Request" in line):
            requests.append(int(line.split("-")[1]))
            continue
        if ("[S] Grant" in line):
            if (len(grants) != len(releases)):
                print(f"\nO erro está na linha:\n{line}")
                print(f"Até esta linha houve {len(grants)} grants")
                print(f"Até esta linha houve {len(releases)} releases")
                raise Exception("Invalid log file: invalid grants and releases sequence, there are more grants than releases")
            grants.append(int(line.split("-")[1]))
            continue
        if ("[R] Release" in line):
            if (len(releases) != len(grants) - 1):
                raise Exception("Invalid log file: invalid grants and releases sequence, something is wrong with your releases")
            releases.append(int(line.split("-")[1]))
            continue

    for i in range(len(requests)):
        if (requests[i] != grants[i] or grants[i] != releases[i]):
            raise Exception("Invalid log file: invalid grants and releases sequence")

    print("Log file was successfully validated")

if __name__ == "__main__":
    validate()