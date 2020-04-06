import datetime
import dateutil.parser
import dateutil.rrule
import dateutil.tz
import io
import sys
import json
import pytz

key_one_allowed = ["DTSTART", "SUMMARY", "LOCATION", "RRULE", "TZID"]
key_ignore = ["ATTENDEE"]


def print_event(event):
    print("-" * 80)
    for key, param_value in event.items():
        if key in key_one_allowed:
            print(f"{key} {param_value['params']}: {param_value['value']}")
        elif len(param_value) == 1:
            print(f"{key} {param_value[0]['params']}: {param_value[0]['value']}")
        else:
            print(key)
            for entry in param_value:
                print(f"  {entry['params']}: {entry['value']}")


def recreate_ics_line(key, entry):
    return ";".join([key] + entry["params"]) + ":" + entry["value"]


def get_next_occurance(event, dt_from, dt_to, tzinfos):
    dtstart = recreate_ics_line("DTSTART", event["DTSTART"])

    for param in event["DTSTART"]["params"]:
        if "VALUE=DATE" in param:
            # Ignore whole day events. Should we handle these?
            return []

    rrule = recreate_ics_line("RRULE", event["RRULE"])
    rrulestr = "\n".join([dtstart, rrule])

    ruleset = dateutil.rrule.rrulestr(rrulestr, forceset=True)

    # Handle excluded dates
    for exdate in event.get("EXDATE", []):
        default_date = datetime.datetime.combine(
            dt_from, datetime.time(0, tzinfo=dateutil.tz.gettz("Europe/London"))
        )
        for param in exdate["params"]:
            key, value = param.split("=", 1)
            if value in tzinfos.keys():
                default_date = datetime.datetime.combine(
                    dt_from, datetime.time(0, tzinfo=tzinfos.get(tzid=value))
                )

        exdate_dt = dateutil.parser.parse(exdate["value"], default=default_date)
        ruleset.exdate(exdate_dt)

    try:
        occurances = ruleset.between(dt_from, dt_to)
    except TypeError as e:
        print_event(event)
        print(dtstart)
        print(rrule)
        raise e

    if occurances:
        new_events = []
        for occurance in occurances:
            new_event = event.copy()
            new_event["DTSTART"] = {"params": [], "value": occurance}
            new_events.append(new_event)

        return new_events
    else:
        return []


def main(dt_from, dt_to):
    capline = ""
    in_event = False
    in_timezone = False
    events = []
    timezones_raw = []
    event = {}

    for line in sys.stdin.readlines():
        if line.startswith(" "):
            capline += line.strip()
        else:
            if capline.startswith("BEGIN:VEVENT"):
                in_event = True

            elif capline.startswith("BEGIN:VTIMEZONE"):
                in_timezone = True
                timezones_raw.append(capline)

            elif in_timezone:
                if capline.startswith("END:VTIMEZONE"):
                    in_timezone = False
                    timezones_raw.append(capline)
                    event = {}
                elif "X-LIC-LOCATION" in capline:
                    # Unsupported property
                    pass
                else:
                    timezones_raw.append(capline)

            elif in_event:
                if capline.startswith("END:VEVENT"):
                    in_event = False
                    events.append(event.copy())
                    event = {}

                else:
                    key_with_params, value = capline.strip().split(":", 1)
                    key, *params = key_with_params.split(";")

                    new_value = {"params": params, "value": value}
                    if key in key_one_allowed:
                        event[key] = new_value
                    elif key not in key_ignore:
                        if not key in event:
                            event[key] = []
                        event[key].append(new_value)

            capline = line.strip()

    timezones_buf = io.StringIO("\n".join(timezones_raw))
    tzinfos = dateutil.tz.tzical(timezones_buf)

    expanded_events = []
    for event in events:
        if not "RRULE" in event:
            event["RRULE"] = {"params": [], "value": "FREQ=DAILY;COUNT=1"}

        if not "LOCATION" in event:
            event["LOCATION"] = {"params": [], "value": ""}

        expanded_events += get_next_occurance(event, dt_from, dt_to, tzinfos)

    events = expanded_events
    events.sort(key=lambda x: x["DTSTART"]["value"])

    json_events = []
    for event in events:
        event["DTSTART"]["value"] = event["DTSTART"]["value"].astimezone(
            pytz.timezone("Europe/London")
        )
        json_events.append(
            {
                "start": event["DTSTART"]["value"].strftime("%Y-%m-%d %H:%M"),
                "start_ts": int(event["DTSTART"]["value"].timestamp()),
                "summary": event["SUMMARY"]["value"],
                "location": event["LOCATION"]["value"],
            }
        )

    print(json.dumps(json_events, indent=2))


if __name__ == "__main__":
    future_days = 10
    if len(sys.argv) > 1:
        future_days = int(sys.argv[1])

    # now = datetime.datetime.now() - datetime.timedelta(hours=1)
    now = datetime.datetime.now(pytz.utc) - datetime.timedelta(hours=1)
    now_plus_n_days = now + datetime.timedelta(days=future_days)
    main(now, now_plus_n_days)
