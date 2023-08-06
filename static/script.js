document.addEventListener('DOMContentLoaded', function() {
  fetch('https://hotelsoffers-recommender.altancabal.repl.co/get-top-hotel')
    .then(response => response.json())
    .then(data => {
      document.getElementById("hotel-img").src = data.img_url;
      document.getElementById("hotel-img").alt = data.name;
      document.getElementById("hotel-name").innerText = data.name;
      document.getElementById("hotel-rating").innerText = `${data.rating}`;
      document.getElementById("hotel-opinion").innerText = `Basado en ${data.opinion_count}`;
      document.getElementById("hotel-price").innerText = `Precio por noche: $${data.price}`;
      document.getElementById("hotel-location").innerText = `Ubicación: ${data.location}`;
      document.getElementById("hotel-url").href = data.url;
      document.getElementById("hotel-url").target = "_blank";
    })
    .catch(error => console.error('An error occurred:', error));
});