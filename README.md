# Next Holiday Sensor

This sensor tells you what holiday is coming up next. You can use it
to set holiday light colors or other scenes. 

The state of the sensor tells you what the upcoming holiday is. There
are sensor attributes showing all the holidays for the year. 

Holidays are recomputed every year. In the config you can specify
what holidays you want to track. The holidays and config are based on
the https://github.com/dr-prodigy/python-holidays

![An example screenshot](screenshot.png)

## Configuration

Add a sensor to your configuration along the lines of:

    sensor:
      - platform: next_holiday
        sources: 
         - country: "USA"
           state: "WA"
         - country: "Israel"
           multiday: false
           filter:
             - 'hanukkah'

This loads all normal holidays for the US State of Washington and also
throws in Hanukkah by loading the Israel holidays. 
