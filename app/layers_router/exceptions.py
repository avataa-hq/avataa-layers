class LayerException(Exception):
    def __init__(self, detail, status_code=None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

    def __str__(self):
        if self.status_code:
            return f"[Error {self.status_code}]: {self.detail}"
        return self.detail


__all__ = ["LayerException"]


class FolderNotExists(LayerException):
    pass


class LayerAlreadyExists(LayerException):
    pass


class LayerDoesNotExists(LayerException):
    pass


class NotAvailableGeoFileType(LayerException):
    pass


class FileAndLinkUploaded(LayerException):
    pass


class FileOrLinkNotUploaded(LayerException):
    pass
