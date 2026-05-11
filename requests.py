import datetime


def get_requests() -> list[list[str|int|datetime.datetime]]:
    """
    Gets all unfullfilled requests from requests file.

    Returns:
        list[list]. List of requests in the format of [[requesterId: int, mediaTitle: str, url: str, comment: str, createdOn: datetime.datetime], ...]
    """
    requests = []

    # open requests file
    with open("requests.csv", "r") as reader:
        line = reader.readline()[:-1]

        while line:
            # add each line to requests list
            requests.append(line.split(","))
            line = reader.readline()[:-1]
        # end
    # end

    # convert requesterId to integer
    # convert created date to datetime object
    for i in range(len(requests)):
        requests[i][0] = int(requests[i][0])
        requests[i][4] = datetime.datetime.strptime(requests[i][4], "%m-%d-%y")
    # end

    return requests
# end


def add_request(requesterId: int, mediaTitle: str, url: str, comment: str, createdAt: datetime.datetime):
    """
    Adds the given media request to the requests file.

    Arguments:
        requesterId (int): The dicord id of the person that made the request.
        mediaTitle (str): The title of the media the person wants downloaded.
        url (str): A url of a webpage with information on the media.
        comment (str): A user given comment.
        createdAt (datetime.datetime): A datetime object when the request was created.
    """

    # get the current requests
    requests = get_requests()

    convertedRequests = []
    # convert requesterIds to a string
    for i in range(len(requests)):
        requests[i][0] = str(requests[i][0])
        convertedRequests.append(requests[i])
    # end

    # add the given request to the current requests
    convertedRequests.append([str(requesterId), mediaTitle, url, comment, createdAt.strftime("%m-%d-%y")])

    # save changes to the requests file
    with open("requests.csv", "w") as writer:
        writer.write("\n".join([",".join(currRequest) for currRequest in convertedRequests]))
    # end
# end