from typeDefs.websocket import wsBaseRet


def constructRouteNotFound() -> wsBaseRet:
    routeNotFound: wsBaseRet = {
        "success": False,
        "code": -1,
        "data": {"message": "Method not found."},
    }
    return routeNotFound
