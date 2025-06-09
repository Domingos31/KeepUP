document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
  
    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      selectable: true,
      editable: true,
  
      select: function (info) {
        const title = prompt('Título do evento:');
        if (title) {
          const color = prompt('Cor do evento (ex: red, green, blue):', 'blue');
          calendar.addEvent({
            title: title,
            start: info.startStr,
            end: info.endStr,
            allDay: info.allDay,
            color: color
          });
        }
        calendar.unselect();
      }
    });
  
    calendar.render();
  });
  