class Reading:
    reading_date: str
    meter_reading: float

    # reading_date will later be a date
    def __init__(self, reading_date: str, meter_reading: float) -> None:
        self.reading_date = reading_date
        self.meter_reading = meter_reading

    def __repr__(self) -> str:
        return f"Reading('{self.reading_date}', '{self.meter_reading}')"
