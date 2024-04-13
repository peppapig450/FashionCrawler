from datetime import datetime, timedelta


class Utils:
    @classmethod
    def convert_to_datetime(cls, time_str_list):
        datetime_list = []

        for time_str in time_str_list:
            parts = time_str.split(" ")
            num = int(parts[0])
            unit = parts[1]

            if unit in ("days", "day"):
                delta = timedelta(days=num)
                format = "%a, %B %d"
            elif unit in ("hours", "hour"):
                delta = timedelta(hours=num)
                format = "%a, %B %d at about %I%p"
            elif unit in ("minutes", "minute"):
                delta = timedelta(minutes=num)
                format = "%a, %B %d at %I:%M%p"
            else:
                raise ValueError("Invalid unit")

            datetime_string = datetime.now() - delta
            formatted_string = datetime_string.strftime(format)
            datetime_list.append(formatted_string)

        return datetime_list
