from datetime import datetime
from dataclasses import dataclass


@dataclass
class Sample:
    id: int
    created: datetime
    humidity: float
    temperature: float
    humidifier_state: int
    fan_state: int
    lights_state: int
    greenhouse_id: int
