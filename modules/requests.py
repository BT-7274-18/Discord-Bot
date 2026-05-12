import datetime, os, csv
from typing import TypedDict


# class for typing requests dict
class Request(TypedDict):
    """
    requesterId: int,
    mediaTitle: str,
    url: str,
    comment: str,
    createdOn: datetime.datetime,
    """

    requesterId: int
    mediaTitle: str
    url: str
    comment: str
    createdOn: datetime.datetime
    requestId: int
# end


def generate_id(currentIds: list[int]) -> int:
    """
    Generates a unique id based on existing id's.

    Arguments:
        currentIds (list[int]): A list of id's that are already taken.

    Returns:
        int: An id that is not in the given list of id's.
    """

    newId: int
    for i in range(len(currentIds) + 1):
        if not i in currentIds: newId = i
    # end

    return newId # type: ignore
# end


def convert_to_typed_dict(data: csv.DictReader[str]) -> list[Request]:
    """
    Converts a csv.DictReader object to a list of Request dicts for type checking.

    Arguments:
        data (csv.DictReader[str]): A dict reader object reading from the requests file.

    Returns:
        list[Request[
            "requesterId": int, 
            "mediaTitle": str, 
            "url": str, 
            "comment": str, 
            "createdOn": datetime.datetime
        ]]: 
        A list of dicts containing requests.
    """

    convertedDicts = []

    for row in data:
        convertedDicts.append(Request(
            requesterId=int(row["requesterId"]),
            mediaTitle=row["mediaTitle"],
            url=row["url"],
            comment=row["comment"],
            createdOn=datetime.datetime.strptime(row["createdOn"], "%m-%d-%y"),
            requestId=int(row["requestId"])
        ))
    # end

    return convertedDicts
# end


def flatten_requests(data: list[Request]) -> list[dict[str, str]]:
    """
    Converts a list of Request TypedDicts into normal dicts.

    Arguments:
        data: list[Request]: A list of TypedDicts to convert to normal dicts.

    Returns:
        list[dict[str, str]]: A list of normal dicts.
    """

    flattenedRequests: list[dict[str, str]] = []

    for request in data:
        flattenedRequest = {}
        for key in request.keys():
            flattenedRequest[key] = request[key].strftime("%m-%d-%y") if type(request[key]) == datetime.datetime else str(request[key])
        # end

        flattenedRequests.append(flattenedRequest)
    # end

    return flattenedRequests
# end

def save_requests(data: list[Request]):
    """
    Writes the give request data to file

    Arguments:
        data (list[Request]): A list of requests dicts
    """

    flattendRequests = flatten_requests(data)

    # save changes to the requests file
    with open("requests.csv", "w") as writer:
        # create csv writter
        writer = csv.DictWriter(writer, fieldnames=data[0].keys())
        # writer csv headers
        writer.writeheader()
        # write request data
        writer.writerows(flattendRequests)
    # end
# end


def get_requests() -> list[Request]:
    """
    Gets all unfullfilled requests from requests file.

    Returns:
        list[Request[
            "requesterId": int, 
            "mediaTitle": str, 
            "url": str, 
            "comment": str, 
            "createdOn": datetime.datetime
            "requestId": int
        ]]: 
        A list of dicts containing requests.
    """
    
    # create a requests file with headers if none exists
    if not os.path.exists("requests.csv"):
        with open("requests.csv", "w") as writer:
            writer.write("requesterId,mediaTitle,url,comment,createdOn,requestId")
        # end
    # end

    # open requests file
    with open("requests.csv", "r") as reader:
        requests = convert_to_typed_dict(csv.DictReader(reader))
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

    # add the given request to the current requests
    requests.append(Request(
        requesterId=requesterId,
        mediaTitle=mediaTitle,
        url=url,
        comment=comment,
        createdOn=createdAt,
        requestId=generate_id([request["requestId"] for request in requests])
    ))

    save_requests(requests)
# end


def remove_request(id: int):
    """
    Removes a request from the requests file with the given id.

    Arguments:
        id (int): The id of the request to be removed.
    """

    # get the current requests
    requests = get_requests()

    # look for the request with the given id
    for i in range(len(requests)):
        if requests[i]["requestId"] == id:
            # remove the request with the given id
            requests.pop(i)
            break
        # end
    # end

    # save changes
    save_requests(requests)
# end


if __name__ == "__main__":
    pass
# end
