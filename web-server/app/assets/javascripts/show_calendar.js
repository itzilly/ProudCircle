document.querySelectorAll('.news-date').forEach(function(element) {
    var date = element.dataset.date;
    var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    var dateString = new Date(date).toLocaleDateString(undefined, options);
    element.setAttribute('title', dateString);
    var calendar = document.createElement('div');
    calendar.classList.add('calendar');
    calendar.textContent = dateString;
    element.appendChild(calendar);
});
