class PostNotFoundError(Exception):
    pass


class PostPermissionDeniedError(Exception):
    pass


class CommentNotFoundError(Exception):
    pass


class PostLikePostNotFoundError(Exception):
    pass


class PostAlreadyLikedError(Exception):
    pass


class PostLikeNotRegisteredError(Exception):
    pass
