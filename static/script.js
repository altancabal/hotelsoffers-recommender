document.addEventListener('DOMContentLoaded', function () {
    const loadingScreen = document.getElementById('loadingScreen');
    setTimeout(() => {
        fetch('https://hotelsoffers-recommender.altancabal.repl.co/get-top-hotel')
            .then(response => response.json())
            .then(data => {
                document.getElementById("hotel-img").src = data.img_url;
                document.getElementById("hotel-img").alt = data.name;
                document.getElementById("hotel-name").innerText = data.name;
                document.getElementById("hotel-rating").innerText = `${data.rating}`;
                document.getElementById("hotel-opinion").innerText = `Basado en ${data.opinion_count}`;
                document.getElementById("hotel-price-value").innerText = `$${data.price}`;
                document.getElementById("hotel-location").innerText = `Costa Rica`;
                document.getElementById("hotel-url").href = data.url;
                document.getElementById("hotel-url").target = "_blank";
                document.getElementById("more-images-link").href = data.url;
                document.getElementById("more-images-link").target = "_blank";

                // Convert dates to Spanish text representation
                const startDate = new Date(data.start_date);
                const endDate = new Date(data.end_date);
                const startDateStr = startDate.toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
                const endDateStr = endDate.toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
              
                document.getElementById("hotel-dates").innerText = `Del ${startDateStr} al ${endDateStr}`;

                loadingScreen.style.opacity = '0';
                loadingScreen.style.pointerEvents = 'none';
            })
            .catch(error => console.error('An error occurred:', error));
    }, 3000); //Wait 3 seconds to display the main screen
});

document.addEventListener('DOMContentLoaded', function() {
  const loadingScreen = document.getElementById('loadingScreen');
  // Existing fetch logic here
  const elems = document.querySelectorAll('.collapsible');
  const instances = M.Collapsible.init(elems);
});
