import os
import logging

import pandas as pd
from todoist.api import TodoistAPI
logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger("main")

TODOIST_TOKEN = os.getenv('TODOIST_TOKEN')

if TODOIST_TOKEN is None:
    LOGGER.error("TODOIST_TOKEN env is not set")
    exit(1)

LOGGER.info("Syncing Todoist ...")
api = TodoistAPI(TODOIST_TOKEN)
api.sync()
LOGGER.info("Synced...")

# The API limits 100 activities to be retrieved per call, so a loop is needed

# Items are retrieved in descending order by date.
# offset indicates how many items should be skipped
activity_list = []
limit = 100
offset = 0

while True:
    LOGGER.info(f"Getting activities, batch {int((offset+100)/100)}")
    # API call, retrieving between 0 and 100 activities
    activities = api.activity.get(limit=limit, offset=offset)

    if not activities['events']: # if it returns an empty list, get out of the loop
      break

    activity_list.extend(activities['events'])

    # set offset to skip the number of rows that were just returned
    offset += limit

# Put 'extra_data' dict on parent dict level, then deletes it
for activity in activity_list:
    activity.update(activity['extra_data'])
    del activity['extra_data']

# Creates DataFrame from activity_list
df_activity = pd.DataFrame(activity_list, columns=['event_date', 'event_type', 'content', 'name'])
print(df_activity.columns)

print(df_activity.head())
