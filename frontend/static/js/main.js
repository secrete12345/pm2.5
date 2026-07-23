document.addEventListener('DOMContentLoaded', () => {
    const aqiContainer = document.getElementById('aqiContainer');
    
    if (aqiContainer && aqiContainer.dataset.pm25) {
        const pm25Value = parseFloat(aqiContainer.dataset.pm25);
        console.log('PM2.5 Value:', pm25Value);
        
        const div = document.getElementById("level");
        div.classList.add("aqi-status"); // Optional: add class for CSS styling
    
        if (pm25Value <= 50) {
            div.textContent += "Good";
            div.style.color = "green";
        } else if (pm25Value <= 100) {
            div.textContent += "Moderate";
            div.style.color = "gold";
        } else if (pm25Value <= 150) {
            div.textContent += "Unhealthy for Sensitive Groups";
            div.style.color = "orange";
        } else if (pm25Value <= 200) {
            div.textContent += "Unhealthy";
            div.style.color = "red";
        } else if (pm25Value <= 300) {
            div.textContent += "Very Unhealthy";
            div.style.color = "purple";
        } else {
            div.textContent += "Hazardous";
            div.style.color = "brown";
        }
    }
});