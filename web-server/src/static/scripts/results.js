const table = document.querySelector('table');
const rows = Array.from(table.querySelectorAll('tr')).slice(1);

function sortTable(columnIndex, ascending) {
  rows.sort((a, b) => {
    const aValue = a.querySelectorAll('td')[columnIndex].textContent;
    const bValue = b.querySelectorAll('td')[columnIndex].textContent;

    if (columnIndex === 0) {
      const aDate = new Date(aValue);
      const bDate = new Date(bValue);
      return ascending ? aDate - bDate : bDate - aDate;
    } else {
      const aNumber = parseInt(aValue.replace(/,/g, ''));
      const bNumber = parseInt(bValue.replace(/,/g, ''));
      return ascending ? aNumber - bNumber : bNumber - aNumber;
    }
  });

  // Remove existing rows from the table
  const tbody = table.querySelector('tbody');
  while (tbody.firstChild) {
    tbody.removeChild(tbody.firstChild);
  }

  // Add the sorted rows to the table
  rows.forEach(row => tbody.appendChild(row));
}

document.getElementById('sort-date-asc').addEventListener('click', () => {
  sortTable(0, true);
});

document.getElementById('sort-date-desc').addEventListener('click', () => {
  sortTable(0, false);
});

document.getElementById('sort-amount-asc').addEventListener('click', () => {
  sortTable(1, true);
});

document.getElementById('sort-amount-desc').addEventListener('click', () => {
  sortTable(1, false);
});
