"""No-op seat: the non-mirror price probe required by bench trap E73 (mirrored sell streams pin MILK/WOOL at floor)."""


def agent(observation, configuration=None):
    return {}
