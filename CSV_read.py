

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
    categories = []
    keywords = []
    order = []

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
            # get rid of any whitespace in rows
            # for each item in the row list
            for x in range(0, len(row)):
                # remove the whitespace before and after any text
                row[x] = row[x].strip()
            # if the item in the row is all uppercase but not the END line
            if row[0].isupper() and row[0] != 'END':
                # set the flag to the all caps title
                flag = row[0]
                # reset the row count
                rowcount = 0
                # reset the space row count
                spacerowcount = 0
            # if the row contains the END line
            if row[0] == 'END':
                # end the read loop
                break
            if flag == 'CATEGORIES' and rowcount > 0:
                categories.append(row[0])
            if flag == 'ORDER' and rowcount > 0:
                order.append(row[0])
            # adds the type of transaction and the keyword to the keyword object.  This is a type list with type
            # string inside
            if flag == 'KEYWORDS' and rowcount > 0:
                # adds the keyword pair to the keyword object
                keywords.append([row[0], row[1]])
                # set the spacerowcount to zero since we read good data
                spacerowcount = 0

    return categories, order, keywords, spacerowcount


def read_data(filepath, categories, keywords):
    """
    This function reads the data csv file that has all the transactions in it.  It must be of the form:
    MM/DD/YYYY, transaction title, withdrawals, deposits

    :param filepath:
    :return: data

    """

    # open file to be read
    with open(filepath, 'r+') as read_file:
        # assign the file to be read to an object
        reader = csv.reader(read_file)
        rowcount = 0

        data = []
        new_keywords = []
        # for each row in the read file
        for row in reader:
            # if the row is blank, skip that iteration of the for loop
            if len(row) == 0:

                continue
            # get rid of any whitespace in rows
            for x in range(0, len(row)):
                row[x] = row[x].strip()
            # set a flag to trigger if a match is found so it stops iterating
            flag = 0
            # for each keyword pair found in the config file
            for x in range(0, len(keywords)):
                # if the words in the keyword pair match the word in the read file
                # the and flag==0 makes sure that it stops looking for a match right after it finds one
                if keywords[x][1].casefold() == row[1].casefold() and flag == 0:
                    # add the category into a new column on the data file
                    row.append(keywords[x][0])
                    # add this new row with the new column to a variable called data
                    data.append(row)
                    # set the flag to one to say that we found a match
                    flag = 1
            # if there was no match
            if flag == 0:
                # ask the user what the transaction was that it didn't recognize
                # add a negative to the value for user to see
                if row[3] == '':
                    # add a negative to the value
                    row[2] = '-' + str(row[2])
                row.remove('')
                print('UNKNOWN TRANSACTION: ' + row[1] + ' ' + row[2])
                new = input('Please enter a category for this transaction: ')
                # remove white spaces from new input
                new = new.strip()
                if new == "skip":
                    continue
                # add this new column onto the row
                row.append(new)
                # add this new row with the new column onto the data
                data.append(row)
                # add the new keyword and category together
                y = [new, row[1]]
                # add this new pair into the temporary keywords object
                keywords.append(y)
                # add this new pair into the new keywords object so that it can get permanently written into the config
                # file
                new_keywords.append(y)

    # for each line of data
    for x in range(0, len(data)):
        # if there is blank space in the deposit column
        if data[x][3] == '':
            # add a negative to the value
            data[x][2] = '-' + str(data[x][2])
        # remove the blank value whether it is in the withdrawal or deposit section to make the data uniform
        if len(data) > 0:
            data[x].remove('')

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
            writer.writerow([row[1], row[0], row[2], row[4]])


def learn_keywords(filepath, new_keywords):
    """
    takes the new keywords that the user input during the read_data function
    :param filepath:
    :param new_keywords:
    :return:
    """
    # open the config file in appending mode so you can only write to the end of it and not disrupt the previous data
    with open(filepath, 'a') as append_file:
        # assign the file to be appended to as an object
        appender = csv.writer(append_file, lineterminator = '\n')
        appender.writerow('')
        # for each new keyword pair that was input by the user
        for x in range(0, len(new_keywords)):
            # write this pair into the config file
            appender.writerow(new_keywords[x])

#define config file location and read it to obtain parameters used for sorting transaction data
CONFIG_FILEPATH = r'C:\Users\bwcon\Documents\PyCharm Projects\Easy Budget\easy_budget_config.csv'
categories, order, keywords, spacerowcount = read_config(CONFIG_FILEPATH)

DATA_FILEPATH = r'C:\Users\bwcon\Documents\PyCharm Projects\Easy Budget\accountactivity.csv'
data, new_keywords = read_data(DATA_FILEPATH, categories, keywords)

WRITE_FILEPATH = r'C:\Users\bwcon\Documents\PyCharm Projects\Easy Budget\Data'
write_data(WRITE_FILEPATH, data)

learn_keywords(CONFIG_FILEPATH, new_keywords)



print('done')