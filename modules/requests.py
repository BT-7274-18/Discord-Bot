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
            createdOn=row["createdOn"] # type: ignore
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
        for key in request.keys():
            flattenedRequests.append({key: str(request[key]) if not type(request[key]) == datetime.datetime else request[key].strftime("%m-%d-%y")})
        # end
    # end

    return flattenedRequests
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
        ]]: 
        A list of dicts containing requests.
    """
    
    # create a requests file with headers if none exists
    if not os.path.exists("requests.csv"):
        with open("requests.csv", "w") as writer:
            writer.write("requesterId,mediaTitle,url,comment,createdOn")
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
    requests.append(Request(requesterId=requesterId, mediaTitle=mediaTitle, url=url, comment=comment, createdOn=createdAt))

    # save changes to the requests file
    with open("requests.csv", "w") as writer:
        # create csv writter
        writer = csv.DictWriter(writer, fieldnames=requests[0].keys())
        # writer csv headers
        writer.writeheader()
        # write request data
        writer.writerows(requests)
    # end
# end