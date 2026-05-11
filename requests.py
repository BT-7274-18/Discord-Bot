def get_requests() -> list[list[str|int]]:
    """
    Gets all unfullfilled requests from requests file.

    Returns:
        list[list[str]]. List of requests in the format of [[requesterId, mediaTitle, url, comment], ...]
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
    for i in range(len(requests)):
        requests[i][0] = int(requests[i][0])
    # end

    return requests
# end


def add_request(requesterId: int, mediaTitle: str, url: str, comment: str):
    """
    Adds the given media request to the requests file.

    Arguments:
        request (list[str]): A media request in the format of [requesterId, mediaTitle, url, comment].
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
    convertedRequests.append([str(requesterId), mediaTitle, url, comment])

    # save changes to the requests file
    with open("requests.csv", "w") as writer:
        writer.write("\n".join([",".join(currRequest) for currRequest in convertedRequests]))
    # end
# end