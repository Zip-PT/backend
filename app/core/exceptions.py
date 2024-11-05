class LocationAPIError(Exception):
    def __init__(self, message: str, api_name: str):
        self.message = message
        self.api_name = api_name
        super().__init__(self.message)
