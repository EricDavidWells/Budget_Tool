

import csv
import datetime
import os.path

def read_config(filepath):
    """
    reads the config file and changes the global variables 'categories' and 'order' for future use

    :param filepath
    :returns categories, order
    """

    # preallocate stuff
    keywords = []

    # open config file and read it
    with open(filepath, 'r+') as config_file:
        #create config file object
        config = csv.reader(config_file)
        writer = csv.writer(config_file)
        spacerowcount = 0
        rowcount = 0
        flag = ''
        #for each row in the config file
        for row in config:

            # get rid of rows with nothing in it, this avoids errors trying to call row[0] when it is only one thing
            # long for some reason it is a string not a list with one value
            if len(row) == 0:
                # add a count to the whitespace row count, note that this resets if we read good data
                # it is just there to count how many spaces there are after the data is read
                spacerowcount += 1
                continue
            # get rid of any empty whitespace rows
            # set whitespace flag so we can escape for iteration when whitespace is detected
            wflag = 0
            # for each item in the row list
            for x in range(0, len(row)):
                # if the section is only whitespace
                if row[x].isspace():
                    # set whitespace flag to one to escape loop
                    wflag = 1
            # if the whitespace flag is one
            if wflag == 1:
                # increment the whitespace row count
                spacerowcount += 1
                # escape the loop
                continue
            # if the row contains information increment the row count
            rowcount += 1
            # for each item in the row list
            for x in range(0, len(row)):
                # remove the whitespace before and after any text
                row[x] = row[x].strip()
            # if the item in the row is all uppercase but not the END line
            if row[0].isupper() and row[0]:
                # set the flag to the all caps title
                flag = row[0]
                # reset the row count
                rowcount = 0
                # reset the space row count
                spacerowcount = 0
            # adds the type of transaction and the keyword to the keyword object.  This is a type list with type
            # string inside
            if flag == 'KEYWORDS' and rowcount > 0:
                # adds the keyword pair to the keyword object
                keywords.append([row[0], row[1]])
                # set the spacerowcount to zero since we read good data
                spacerowcount = 0

    return keywords, spacerowcount


def read_data(filepath, keywords):
    """
    This function reads the data csv file that has all the transactions in it.  It must be of the form:
    MM/DD/YYYY, transaction title, withdrawals, deposits

    :param filepath:
    :return: data

    """

    with open(filepath, 'r+') as read_file:      # open file to be read
        reader = csv.reader(read_file)      # assign the file to be read to an object
        data = []
        new_keywords = []
        for row in reader:      # for each row in the read file
            if len(row) == 0:       # if the row is blank, skip that iteration of the for loop
                continue

            for x in range(0, len(row)):        # get rid of any whitespace in rows
                row[x] = row[x].strip()

            if row[3] == '':        # if the row is a withdrawal
                row[2] = '-' + str(row[2])      # add a negative to the value
            row.remove('')      # remove empty column (withdrawal or deposit)

            flag = 0         # set a flag to trigger if a match is found so it stops iterating
            for x in range(0, len(keywords)):       # for each keyword pair found in the config file

                if keywords[x][1].casefold() == row[1].casefold() and flag == 0:    # if a keyword match is found
                    row.append(keywords[x][0])      # add the category into a new column on the data file
                    data.append(row)        # add this new row with the new column to a variable called data
                    flag = 1        # set the flag to one to say that we found a match

            if flag == 0:       # if there was no match
                # ask the user what the transaction was that it didn't recognize
                print('UNKNOWN TRANSACTION: ' + row[0] + ' ' + row[1] + ' ' + row[2])
                new = input('Please enter a category for this transaction: ')
                new = new.strip()       # remove white spaces from new input
                if new == "skip":       # if user entered skip don't add it to the keyword list
                    continue
                row.append(new)         # add this new column onto the row
                data.append(row)        # add this new row with the new column onto the data
                y = [new, row[1]]       # add the new keyword and category together
                keywords.append(y)      # add this new pair into the keywords object so it gets added to search loop
                new_keywords.append(y)  # add this new pair into the new keywords object to get written to config

    return data, new_keywords


def write_data(filepath, data):
    """
    Makes the date and time and writes the data collected to a file with the date followed by budget.

    :param filepath:
    :param data:
    :return:
    """

    # find the current date for naming our new data file
    date = str(datetime.date.today())
    # all this does is connect the output filepath folder to the new file name, the os.path.join function just does it
    # in a 'smart' way so that you dont have to add all the backslashes and stuff on your own
    filename = os.path.join(filepath, date + '_budget' + '.csv')
    # open the file to be written to, if it doesn't find one it creates one
    with open(filename, 'w') as write_file:
        # assign the file to be written to as an object, for some reason it prints an extra line unelss you define the
        # line terminator to be '\n'
        writer = csv.writer(write_file, lineterminator = '\n')
        # for each row in the data that we previously obtained in reverse order
        for row in data:
            # write a row to the new file in the order: transaction name, date, value, category
            writer.writerow([row[0], row[1], row[2], row[4]])


def learn_keywords(filepath, new_keywords):
    """
    takes the new keywords that the user input during the read_data function
    :param filepath:
    :param new_keywords:
    :return:
    """
    with open(filepath, 'a') as append_file:        # open the config file in appending mode
        for x in range(0, len(new_keywords)):       # for each new keyword
            append_file.write(new_keywords[x][0] + ',' + new_keywords[x][1] + '\n')     # write new keyword to config

def write_to_master(filepath, data):
    """
    takes the data with the category added on and appends it to the master file.  Will check master file to ensure
    that it doesn't write a transaction more than once
    :param filepath:
    :param data:
    :return:
    """

    with open(filepath, 'r+') as read_file:
        reader = csv.reader(read_file)
        most_recent_date = '00/00/0000'
        for row in reader:
            if len(row) == 0:
                continue
            wflag = 0
            for x in range(0, len(row)):
                if row[x].isspace():
                    wflag = 1
            if wflag == 1:
                continue
            datesplit = row[0].split('/')
            date_value = int(datesplit[2])*1000 + int(datesplit[1]) * 100 + int(datesplit[0])
            print(datesplit)
            print(date_value)

# define config file location and read it to obtain parameters used for sorting transaction data
CONFIG_FILEPATH = r'C:\Users\bwcon\Documents\PyCharm Projects\Easy Budget\easy_budget_config.csv'
keywords, spacerowcount = read_config(CONFIG_FILEPATH)

DATA_FILEPATH = r'C:\Users\bwcon\Documents\PyCharm Projects\Easy Budget\accountactivity.csv'
data, new_keywords = read_data(DATA_FILEPATH, keywords)

# WRITE_FILEPATH = r'C:\Users\bwcon\Documents\PyCharm Projects\Easy Budget\Data'
# write_data(WRITE_FILEPATH, data)

MASTER_FILEPATH = r'C:\Users\bwcon\Documents\PyCharm Projects\Easy Budget\Master\master.csv'
learn_keywords(CONFIG_FILEPATH, new_keywords)
write_to_master(MASTER_FILEPATH, data)

print('done')