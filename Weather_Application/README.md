# Weather Application using API Integration

## Overview

The **Weather Application** is a Python console application that retrieves and displays real-time weather information for any city. It uses the OpenWeatherMap API to provide details such as temperature, humidity, wind speed, and current weather conditions.

To ensure the application can be tested without requiring an internet connection or API key, it also includes a built-in mock mode containing weather data for more than 60 Indian cities and several international locations.

The project demonstrates practical implementation of API integration, JSON data processing, file handling, logging, exception handling, and modular programming using only Python's standard library.

## Features

### Real-Time Weather Information

* Retrieve current weather data for any city using the OpenWeatherMap API.
* Display:

  * Temperature
  * Feels-like temperature
  * Humidity
  * Wind speed
  * Weather condition
  * Date and time of retrieval

### Offline Mock Mode

* Built-in weather dataset for over 60 Indian cities.
* Includes several international cities for testing.
* Allows the application to run without an internet connection or API key.
* Useful for demonstrations and development.

### Modular Application Design

The application is organized into separate functional layers:

* **API Layer** – Handles communication with the weather service.
* **Data Processing Layer** – Parses and structures API responses.
* **Display Layer** – Presents weather information in a clear and readable format.

This structure makes the application easier to understand, maintain, and extend.

### User-Friendly Interface

* Interactive menu-driven console application.
* Search weather by city name.
* Switch between Celsius and Fahrenheit.
* Toggle between Mock Mode and Live Mode at any time.

### Search History

* Automatically stores previous searches in a local JSON file.
* Allows users to review recently searched cities.

### Logging

* Records application events with timestamps.
* Displays logs in the console.
* Saves logs to a local `weather_app.log` file for future reference.

### Error Handling

The application handles common errors gracefully, including:

* Invalid or missing API keys
* City not found
* Internet connection or network failures
* Timeout errors
* Invalid API responses

## Technologies Used

* **Python 3**

### Standard Python Libraries

* `urllib.request` – API requests
* `urllib.error` – Network error handling
* `json` – JSON parsing and search history storage
* `logging` – Application logging
* `datetime` – Date and time management

No third-party libraries are required.

## Requirements

* Python 3.8 or later
* Windows, macOS, or Linux
* No additional Python packages required

**Optional**

To use live weather data, obtain a free API key from OpenWeatherMap.


## Installation

1. Install Python 3 if it is not already installed.

```bash
python --version
```

2. Download or clone the project.

3. Open the project folder in your terminal or command prompt.

4. If you want to use live weather data, create a free API key from OpenWeatherMap and add it to the application configuration.

No additional installation steps are required.


## Running the Application

Run the following command from the project directory:

```bash
python weather_app.py
```

By default, the application starts in **Mock Mode**, allowing it to run without internet access.

To use live weather data:

1. Add your OpenWeatherMap API key to the configuration section of the program.
2. Switch from **Mock Mode** to **Live Mode** using the application menu.


## Menu Options

```text
1. Get Weather for a City
2. View Search History
3. Change Temperature Unit (Celsius/Fahrenheit)
4. Switch Between Mock Mode and Live Mode
5. Exit
```


## Sample Output

```text
============================================
        WEATHER APPLICATION
============================================

Mode : Mock
Units: Celsius

1. Get Weather for a City
2. View Search History
3. Change Temperature Unit
4. Switch Data Source
5. Exit

Enter your choice: 1

Enter city name: London

--------------------------------------------
Weather Report
--------------------------------------------
City          : London
Condition     : Light Rain
Temperature   : 17.2 °C
Feels Like    : 17.0 °C
Humidity      : 65%
Wind Speed    : 4.1 m/s
Retrieved At  : 2026-07-05 14:38:14
--------------------------------------------
```

## Project Structure

```text
Weather_Application/
│
├── weather_app.py
├── weather_history.json
├── weather_app.log
└── README.md
```

## Future Enhancements

Possible improvements for future versions include:

* Add a 5-day and 7-day weather forecast
* Support weather search using GPS or current location
* Integrate multiple weather service providers
* Export search history to CSV or Excel
* Display weather charts and graphical reports
* Develop a graphical user interface using Tkinter
* Build a web version using Flask or Django
* Add automated unit testing for improved reliability

## Learning Outcomes

This project provided practical experience in:

* API integration using Python
* HTTP requests and response handling
* JSON data processing
* File handling
* Exception handling
* Logging
* Modular programming
* Console application development
* Working with real-world web services


## Author

**Ardra Rajesh**
Developed as part of the **CODEVEDX Python Programming Internship**.
