# Grazioso Salvare Animal Shelter Dashboard

An interactive dashboard that helps a dog-rescue organization (Grazioso Salvare) find the right dogs for search-and-rescue training. It reads animal-shelter records from MongoDB, filters them by rescue type, and shows the results in a table, a chart, and a map.

## Features

- **Rescue-type filter:** radio buttons (for example Water Rescue and Mountain or Wilderness Rescue) narrow the shelter dogs to those that fit each type of rescue work.
- **Data table:** sortable and filterable records for the matching animals.
- **Chart:** a pie chart of rescue-skill distribution among the filtered animals.
- **Map:** a geolocation map with a marker, tooltip, and popup for each animal.

## How it's built

- **`crud_module.py`**: an `AnimalShelter` class that wraps MongoDB with `create`, `read`, `update`, and `delete`. Every method checks the connection first and fails gracefully, credentials are URL-encoded, and indexes are created on the fields the dashboard filters on most (`animal_type`, `breed`, `outcome_type`).
- **`ProjectTwoDashboard.ipynb`**: the Dash app (Dash, Plotly, dash-leaflet, pandas) that calls the CRUD module and updates the table, chart, and map when the filter changes.
- **Configuration:** database settings come from environment variables, with no credentials in the code: `MONGO_USER`, `MONGO_PASS`, `MONGO_HOST`, `MONGO_PORT`, `MONGO_DB`, `MONGO_COL`.

## What I improved after code review

The first version of the CRUD module only implemented create and read, and it contained stray shell text that stopped it from importing. I removed that, implemented update and delete, added connection guards to every method, URL-encoded the credentials, and added the indexes.

## Run it

You need a running MongoDB instance with the animal data loaded.

```bash
pip install pymongo pandas plotly dash jupyter-dash dash-leaflet
export MONGO_USER=your_user MONGO_PASS=your_password
jupyter lab   # open ProjectTwoDashboard.ipynb and run all cells
```

## Tech stack

Python, MongoDB (PyMongo), Dash, Plotly, dash-leaflet, pandas, Jupyter

## Background

Started as the CS-340 (Client/Server Development) project at SNHU, then enhanced as part of my CS-499 capstone.
