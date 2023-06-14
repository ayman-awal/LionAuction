import csv
import hashlib

with open('Users.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)

    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        for row in reader:
            password = row[1]
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            row[1] = hashed_password

            writer.writerow(row)