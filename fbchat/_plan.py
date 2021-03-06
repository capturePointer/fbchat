import attr
import json
from ._core import attrs_default, Enum
from . import _util


class GuestStatus(Enum):
    INVITED = 1
    GOING = 2
    DECLINED = 3


@attrs_default
class Plan:
    """Represents a plan."""

    #: Plan time (datetime), only precise down to the minute
    time = attr.ib()
    #: Plan title
    title = attr.ib()
    #: ID of the plan
    uid = attr.ib(None)
    #: Plan location name
    location = attr.ib(None, converter=lambda x: x or "")
    #: Plan location ID
    location_id = attr.ib(None, converter=lambda x: x or "")
    #: ID of the plan creator
    author_id = attr.ib(None)
    #: Dictionary of `User` IDs mapped to their `GuestStatus`
    guests = attr.ib(None)

    @property
    def going(self):
        """List of the `User` IDs who will take part in the plan."""
        return [
            id_
            for id_, status in (self.guests or {}).items()
            if status is GuestStatus.GOING
        ]

    @property
    def declined(self):
        """List of the `User` IDs who won't take part in the plan."""
        return [
            id_
            for id_, status in (self.guests or {}).items()
            if status is GuestStatus.DECLINED
        ]

    @property
    def invited(self):
        """List of the `User` IDs who are invited to the plan."""
        return [
            id_
            for id_, status in (self.guests or {}).items()
            if status is GuestStatus.INVITED
        ]

    @classmethod
    def _from_pull(cls, data):
        return cls(
            uid=data.get("event_id"),
            time=_util.seconds_to_datetime(int(data.get("event_time"))),
            title=data.get("event_title"),
            location=data.get("event_location_name"),
            location_id=data.get("event_location_id"),
            author_id=data.get("event_creator_id"),
            guests={
                x["node"]["id"]: GuestStatus[x["guest_list_state"]]
                for x in json.loads(data["guest_state_list"])
            },
        )

    @classmethod
    def _from_fetch(cls, data):
        return cls(
            uid=data.get("oid"),
            time=_util.seconds_to_datetime(data.get("event_time")),
            title=data.get("title"),
            location=data.get("location_name"),
            location_id=str(data["location_id"]) if data.get("location_id") else None,
            author_id=data.get("creator_id"),
            guests={id_: GuestStatus[s] for id_, s in data["event_members"].items()},
        )

    @classmethod
    def _from_graphql(cls, data):
        return cls(
            uid=data.get("id"),
            time=_util.seconds_to_datetime(data.get("time")),
            title=data.get("event_title"),
            location=data.get("location_name"),
            author_id=data["lightweight_event_creator"].get("id"),
            guests={
                x["node"]["id"]: GuestStatus[x["guest_list_state"]]
                for x in data["event_reminder_members"]["edges"]
            },
        )
