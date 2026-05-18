# review-file-app
A lightweight Flask web application that connects to the Sierra REST API and helps staff review and update patron records from a Sierra Review File in a more streamlined interface.

The project began as a proof of concept after Sierra added the ability to query data directly from a review file through the REST API. The original workflow required staff to move back and forth between a shared spreadsheet, Microsoft Teams, Excel, and the Sierra Desktop App. This app demonstrates how a review file can become the starting point for a focused, staff-friendly workflow that retrieves records, displays key patron fields, and supports record updates through the Sierra Patron API.

## Project Background
The Review File App was developed as part of the 2026 IUG Hackathon. The initial use case focused on patron address cleanup, where staff needed a faster way to review patron records, verify contact information, and update selected fields without manually opening each record in Sierra.

Additional workflow ideas include supporting processes such as the Evie patron record update and waive workflow, where staff need to identify a targeted group of records, review item or patron data, and take consistent action across records.

##What the App Does

At a high level, the application:

Connects to the Sierra REST API.
Retrieves records from a selected Sierra Review File.
Uses the returned record IDs to fetch patron record details.
Displays patron information in a web interface.
Allows staff to review and edit selected fields.
Sends updates back to Sierra through the Patron API.

The app is intended as a prototype and demonstration of what can be built by combining Sierra Review Files with the Sierra REST API. It should be reviewed and adapted before use in production.

## Benefits for Staff

The app reduces the need to move between multiple tools during record cleanup projects. Instead of copying data from Sierra into spreadsheets, tracking notes in Teams, and manually opening records one at a time, staff can work from a single web interface.

Key benefits include:

Fewer manual steps.
Less back-and-forth between Sierra, Excel, and Teams.
More consistent review and update workflows.
A clearer interface for project-specific cleanup tasks.
A reusable pattern for future Sierra review file workflows.

## Technology Stack
- Python
- Flask
- Sierra REST API
- HTML/CSS templates
- Environment variables for configuration

## Prerequisites

Before running the application, you will need:

- Python 3.10 or newer
- Access to a Sierra REST API environment
- A Sierra API key and secret
- Permission to read review files
- Permission to read and update patron records, if using the update functionality
- A Sierra Review File containing patron records

## Sierra API Requirements

The application relies on Sierra REST API access. At minimum, the API credentials should support:
- Reading review files
- Reading records from a review file
- Reading patron records
- Updating patron records, if edit functionality is enabled

Common endpoints used by this type of workflow include:

```
/v6/reviewFiles
/v6/reviewFiles/{id}/records
/v6/patrons/{id}
```

Your Sierra API permissions should be scoped as narrowly as possible for the intended workflow.


```

Your Sierra API permissions should be scoped as narrowly as possible for the intended workflow.

