  Weather Forecast Application

Weather Forecast Application 🌦️
================================

Running the Application and Installing Dependencies
---------------------------------------------------

### Dependencies:

*   🏗️ **Flask**: A lightweight WSGI web application framework in Python.
*   📡 **Requests**: A simple, yet elegant HTTP library in Python.
*   💾 **SQLite3**: Used for the local database.

### Installation and Running:

1.  Ensure Python is installed on your system.
2.  Install Flask and Requests if you haven't already:
    
        pip install Flask requests
    
3.  Run the Flask application:
    
        python final.py
    

Short Report 📝
---------------

**Overall Process:** The task involved creating a weather forecast application using Flask, which fetched data from the Meteomatics API, stored it in an SQLite database, and provided various endpoints for data access and visualization. The application needed to handle user inputs for dynamic data querying and ensure data integrity and security.

**Key Decisions:**

*   🌐 API Integration: Chose to integrate the Meteomatics weather API for real-time weather data due to its comprehensive documentation and ease of use.
*   🗃️ Database Choice: Opted for SQLite due to its simplicity and the fact that it requires no separate server process, which suits the scope of this application.
*   🛠️ Flask Framework: Selected for its simplicity in setting up web servers and endpoints, which facilitated quick development and testing.

**Challenges and Solutions:**

*   📊 Data Structure: Determining the most efficient database schema to store and query weather data. Resolved by normalizing data into separate tables for locations and forecasts.
*   🔒 Security: Ensuring the secure storage of API credentials. Resolved by storing credentials outside of the main script and ignoring sensitive files from version control.

**Unexpected Issues:**

*   🕰️ Timezone inconsistencies between the API data and user local time were addressed by converting all times to UTC.

**Problems and Solutions:**

🌡️ **Average Temperature Calculations**: The requirement was to list the average temperature of the last three forecasts for each location, every day. This posed a challenge due to SQLite's limitations in handling complex queries and Python's data processing overhead.

- **Problem**: SQLite does not support some of the more complex SQL operations needed to easily calculate the average of the last three forecasts per day for each location directly in a single query. Additionally, performing this calculation entirely within Python could lead to significant overhead, especially with large datasets.
  
- **Solution**: I approached this problem by breaking it down into manageable steps. First, I extracted all relevant forecasts for each location from the SQLite database, ordered by date. Then, processed this data in Python, organizing it by location and date, and computing the average temperature for the last three forecasts of each day. This approach leveraged SQLite's efficiency in data retrieval and Python's flexibility in data manipulation, offering a balanced solution while adhering to the application's technological stack's capabilities.

This solution illustrates the importance of combining SQL and Python's strengths to overcome the limitations of using SQLite for complex data processing tasks. It also underscores the necessity of clear problem breakdown and iterative solution design in software development.

*   📚 Large Datasets: Handling large datasets and ensuring application performance led to implementing pagination for data displayed on the frontend.

**Tools and Techniques Used:**

*   🖥️ Flask for backend and API management.
*   🎨 HTML/CSS, Bootstrap for frontend styling.
*   📦 SQLite for database management.
*   📂 Git for version control and collaboration.
*   🧪 Postman for API testing and validation.
