
# datelist_countdown

Component for Home Assistant to implement a list of dates for a countdown.
I use this with a list of garbage collection dates.

## Installation

Copy to custom_components/datelist_countdown folder

## Configuration

In configuration.yaml:

    sensor:
      - platform: datelist_countdown
        name: Some dates
        friendly_name: Yet another name
        file_name: "/config/dates.txt"


Contents of /config/dates.txt:

    2020-12-01
    2020-12-31
    2021-01-31
    2021-02-28
    2021-03-30


## Example usage
In combination with custom:button-card:


    type: 'custom:button-card'
    entity: sensor.papiermull
    color_type: card-label
    show_state: true
    show_icon: false
    show_units: false
    show_label: true
    label: '[[[ return `${states[''sensor.papiermull''].attributes[''next'']}` ]]]'
    aspect_ratio: 1/1
    styles:
      state:
        - font-size: 450%
        - margin: auto
      card:
        - background-color: var(--card-background-color)
      grid:
        - grid-template-areas: '"n" "s" "l"'
        - grid-template-columns: 1fr
        - grid-template-rows: min-content 1fr min-content


![](example.png)


To format the date into format "dd.mm.yyyy" as commonly used in Germany, you can use this line inside the code depicted above:

    label: >-
      [[[ var d = new Date(Date.parse(`${states['sensor.papiermull'].attributes['next']}`));
      return ("0" + (d.getDate() + 1)).slice(-2) + "." + ("0" + (d.getMonth() + 1)).slice(-2) + "." + d.getFullYear();
       ]]]
