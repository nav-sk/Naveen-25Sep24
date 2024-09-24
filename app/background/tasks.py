import datetime
from typing import List, Literal, Mapping, Tuple

import pandas as pd
import pytz

from app.models import Report, Store, StoreHours, StoreStatus

from .celery import app
from .params import TaskParams


def get_day_of_week(datetime: datetime.datetime) -> int:
    return datetime.weekday()


def local_to_utc(
    local_time: datetime.time, timezone: str, utc_time_for_date: datetime.datetime
) -> datetime.time:
    local_timezone = pytz.timezone(timezone)
    local_time = local_timezone.localize(
        datetime.datetime.combine(utc_time_for_date.date(), local_time)
    )
    utc_time = local_time.astimezone(pytz.utc)
    return utc_time.time()


def build_report_data_for_store(
    store_id: str,
    store_statuses: List[Tuple[datetime.datetime, Literal["active", "inactive"]]],
    store_hours: List[Tuple[datetime.time, datetime.time]],
    store_timezone: str,
    last_updated_timestamp: datetime.datetime,
):
    # Dividing the statuses of a store into each day based on the timestamp
    # status_per_days = [[(timestamp, status), ...], ...]
    status_per_days: List[
        List[Tuple[datetime.datetime, Literal["active", "inactive"]]]
    ] = list()
    # store_statuses is already sorted based on timestamp
    # logic to divide the statuses into each day
    status_per_days.append([store_statuses[0]])
    i = 0
    for status in range(1, len(store_statuses)):
        if status_per_days[i][0][0].day != store_statuses[status][0].day:
            status_per_days.append([store_statuses[status]])
            i += 1
        else:
            status_per_days[i].append(store_statuses[status])
    # dictionary to store the count of uptime and downtime for last hour, last day and last week
    count_dict = dict(
        uptime_last_hour=0,
        uptime_last_day=0,
        uptime_last_week=0,
        downtime_last_hour=0,
        downtime_last_day=0,
        downtime_last_week=0,
    )
    # iterate over each day and calculate the uptime and downtime
    # to minimize the complexity of calculation, we are considering the time intervals of 15 mins
    for each_day in status_per_days:
        # getting the local start and end time of the store for the particular week day
        (start_time_local, end_time_local) = store_hours[
            get_day_of_week(each_day[0][0])
        ]
        # converting the local start and end time to utc
        # as the status timestamps are in utc
        start_time_utc = local_to_utc(start_time_local, store_timezone, each_day[0][0])
        end_time_utc = local_to_utc(end_time_local, store_timezone, each_day[0][0])
        # filtering the statuses based on the start and end time of the store
        # in order to consider only the statuses during the business hours
        filtered_business_hours = list(
            filter(lambda x: start_time_utc <= x[0] <= end_time_utc, each_day)
        )
        # generating the time intervals of 15 mins for the business hours
        all_time_intervals_of_business_hours: List[datetime.datetime] = []
        current_time = start_time_utc
        while current_time <= end_time_utc:
            all_time_intervals_of_business_hours.append((current_time, None))
            current_time += datetime.timedelta(minutes=15)
        if current_time - datetime.timedelta(minutes=15) < end_time_utc:
            all_time_intervals_of_business_hours.append((end_time_utc, None))
        # append the status from polled data to the time intervals of business hours
        for log in filtered_business_hours:
            all_time_intervals_of_business_hours.append((log[0], log[1]))
        # sort the time intervals based on timestamp
        all_time_intervals_of_business_hours.sort(key=lambda x: x[0])
        # create a pandas series to interpolate the data
        data = pd.Series(
            list(zip(*all_time_intervals_of_business_hours))[1],
            index=list(zip(*all_time_intervals_of_business_hours))[0],
        )
        # interpolate the data to fill the missing values
        interpolated_data = data.fillna(method="ffill")
        interpolated_data = interpolated_data.fillna(method="bfill")
        # calculate the uptime and downtime based on the interpolated data
        # set the last status as None
        last = None
        for current_timestamp, active_status in interpolated_data.to_dict().items():
            # if the last status is None, update the last status as the current timestamp
            if last == None:
                last = current_timestamp
                continue
            # calculate the difference in minutes between the statuses
            difference_in_minutes = (current_timestamp - last).total_seconds() // 60
            # since the data is only for the past week, we are considering only the statuses for the past week
            if active_status == "active":
                count_dict["uptime_last_week"] += difference_in_minutes
            else:
                count_dict["downtime_last_week"] += difference_in_minutes
            # based on the timestamp calculate the uptime and downtime for last hour
            if last_updated_timestamp - current_timestamp <= datetime.timedelta(
                hours=1
            ):
                if active_status == "active":
                    count_dict["uptime_last_hour"] += difference_in_minutes
                else:
                    count_dict["downtime_last_hour"] += difference_in_minutes
            # based on the timestamp calculate the uptime and downtime for last day
            if last_updated_timestamp - current_timestamp <= datetime.timedelta(days=1):
                if active_status == "active":
                    count_dict["uptime_last_day"] += difference_in_minutes
                else:
                    count_dict["downtime_last_day"] += difference_in_minutes
            # update the last timestamp
            last = current_timestamp
            # if the last timestamp is greater than the last updated timestamp, break the loop
            if last > last_updated_timestamp:
                break
    # convert the uptime and downtime for last_day and last_week to hours
    for key in count_dict.keys():
        if "hour" not in key:
            count_dict[key] //= 60
            count_dict[key] = int(count_dict[key])

    count_dict["store_id"] = store_id
    # declaring the final store_data for returning
    store_data = {**count_dict, "store_id": store_id}
    return store_data


def generate_csv_from_dict(data: List[dict]):
    df = pd.DataFrame(data)
    # reordering the columns
    df = df[
        [
            "store_id",
            "uptime_last_hour",
            "uptime_last_day",
            "uptime_last_week",
            "downtime_last_hour",
            "downtime_last_day",
            "downtime_last_week",
        ]
    ]
    # renaming the columns
    df.columns = [
        "store_id",
        "uptime_last_hour (in minutes)",
        "uptime_last_day (in hours)",
        "uptime_last_week (in hours)",
        "downtime_last_hour (in minutes)",
        "downtime_last_day (in hours)",
        "downtime_last_week (in hours)",
    ]
    # storing the data in csv format
    return df.to_csv(index=False, header=True)


@app.task(bind=True)
def generate_report(self, *args, **kwargs):
    # getting the report ID from the task params
    task_params = TaskParams(**kwargs)
    report_id = task_params.report_id
    print("-" * 50)
    print("Generating Report : ", report_id)
    print("-" * 50)
    report = Report.objects.get(report_id=report_id)
    # getting the last updated timestamp in the db
    last_updated_timestamp = (
        StoreStatus.objects.order_by("-timestamp_utc").first().timestamp_utc
    )
    # filter the data in store_statuses for the last 7 days as we are considering only for past week
    store_statuses = StoreStatus.objects.select_related("store").filter(
        timestamp_utc__gte=last_updated_timestamp - datetime.timedelta(days=7)
    )
    # get all the store hours and stores
    store_hours = StoreHours.objects.select_related("store").all()
    stores = Store.objects.all()
    # create a dictionary for mapping store_id and timezone
    stores_timezones: Mapping[str, str] = dict()
    for store in stores:
        stores_timezones[store.store_id] = store.timezone
    # create a dictionary for mapping store_id and store hours
    # store_hours_dict = {store_id: [(start_time, end_time), ...]}
    store_hours_dict: Mapping[str, List[Tuple[datetime.time, datetime.time]]] = dict()
    for store_hour in store_hours:
        if not store_hour.store.store_id in store_hours_dict:
            store_hours_dict[store_hour.store.store_id] = [
                (0, 0)
            ] * 7  # list of tuple of start_time and end_time for each day
        store_hours_dict[store_hour.store.store_id][store_hour.day_of_week] = (
            store_hour.start_time_local,
            store_hour.end_time_local,
        )  # updating the start_time and end_time for each day
    store_hours = store_hours_dict
    # create a dictionary for mapping store_id and store statuses
    # store_statuses_dict = {store_id: [(timestamp_utc, status), ...]}
    store_statuses_dict: Mapping[
        str, List[Tuple[datetime.datetime, Literal["active", "inactive"]]]
    ] = dict()
    for store_status in store_statuses:
        if not store_status.store.store_id in store_statuses_dict:
            store_statuses_dict[store_status.store.store_id] = list()
        store_statuses_dict[store_status.store.store_id].append(
            (store_status.timestamp_utc, store_status.status)
        )
    store_statuses = store_statuses_dict
    # deleting instances to release memory
    del store_hours_dict
    del store_statuses_dict
    del stores
    report_data: List[Mapping[str, int]] = list()
    # iterate over all the stores and generate report data for each store
    for store_id in store_statuses.keys():
        # sort the store statuses based on timestamp
        store_statuses[store_id].sort(key=lambda x: x[0])
        # for each store generate the report data
        store_report_data = build_report_data_for_store(
            store_id=store_id,
            store_statuses=store_statuses[store_id],
            store_hours=store_hours[store_id],
            store_timezone=stores_timezones[store_id],
            last_updated_timestamp=last_updated_timestamp,
        )
        # append the report data to the report_data list
        report_data.append(store_report_data)

    # generate csv from the report data
    csv_data: str = generate_csv_from_dict(report_data)
    report.report = csv_data
    report.status = "Complete"
    report.save()  # saving to db
    print("-" * 50)
    print("Report Generated : ", report_id)
    print("-" * 50)
