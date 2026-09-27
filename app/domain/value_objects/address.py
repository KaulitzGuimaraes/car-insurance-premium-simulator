class Address:
    def __init__(
        self,
        city: str,
        country: str,
        state: str,
    ):
        if not city:
            raise ValueError("City cannot be empty")

        if not country:
            raise ValueError("Country cannot be empty")

        if not state:
            raise ValueError("State cannot be empty")

        self._city = city
        self._country = country
        self._state = state

    @property
    def city(self) -> str:
        return self._city

    @property
    def country(self) -> str:
        return self._country

    @property
    def state(self) -> str:
        return self._state
